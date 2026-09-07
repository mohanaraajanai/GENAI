from __future__ import annotations

from typing import Any, TypedDict

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, START, StateGraph

from .prompts import GENERATION_PROMPT, SYSTEM_PROMPT
from .web_search import WebSearchService


class RAGServiceError(RuntimeError):
    """Safe application error with a customer-friendly message.

    The technical exception is retained separately so the UI does not expose
    API keys, organization IDs, request details, or raw provider responses.
    """

    def __init__(self, kind: str, user_message: str, technical_message: str = ""):
        super().__init__(technical_message or user_message)
        self.kind = kind
        self.user_message = user_message
        self.technical_message = technical_message or user_message


def _classify_llm_error(exc: Exception) -> RAGServiceError:
    """Map provider errors to safe messages without making another API call."""
    text = str(exc).lower()
    status = getattr(exc, "status_code", None)

    if status == 429 or "rate limit" in text or "requests per day" in text or "rate_limit_exceeded" in text:
        return RAGServiceError(
            "rate_limit",
            "The AI service is temporarily unavailable because its usage limit has been reached. "
            "Please try again later.",
            str(exc),
        )

    if "insufficient_quota" in text or "quota" in text or "billing" in text or "payment" in text:
        return RAGServiceError(
            "quota",
            "The AI service is temporarily unavailable because its usage quota has been reached. "
            "Please try again later.",
            str(exc),
        )

    if status in (401, 403) or "invalid api key" in text or "authentication" in text:
        return RAGServiceError(
            "authentication",
            "The AI service configuration needs attention. Please contact the application administrator.",
            str(exc),
        )

    if "timeout" in text or "timed out" in text or "deadline" in text:
        return RAGServiceError(
            "timeout",
            "The AI service took too long to respond. Please try again in a moment.",
            str(exc),
        )

    return RAGServiceError(
        "llm_error",
        "The adviser could not complete the request right now. Please try again later.",
        str(exc),
    )


class State(TypedDict, total=False):
    question: str
    history: list[dict[str, str]]
    query: str
    scope: str
    documents: list[Document]
    retrieval_scores: list[float]
    web_results: list[dict[str, Any]]
    answer: str
    retry_count: int
    web_used: bool
    web_error: str
    supported: bool
    answers_question: bool
    grade_reason: str
    source_mode: str
    sources: list[dict[str, str]]


class SelfRAG:
    """Low-request Self-RAG with local routing and retrieval-confidence gating.

    Normal path:
        local scope -> FAISS retrieval -> confidence gate -> one LLM generation

    Fallback path:
        local scope -> FAISS retrieval -> weak/no evidence -> Tavily -> one LLM generation

    No LLM is used for scope classification, document grading, query rewriting,
    or answer grading. This keeps the normal request footprint low.
    """

    def __init__(
        self,
        vector_store,
        llm,
        web_search: WebSearchService | None = None,
        k: int = 4,
        relevance_threshold: float = 0.35,
    ):
        self.vector_store = vector_store
        self.llm = llm
        self.web_search = web_search or WebSearchService()
        self.k = k
        self.relevance_threshold = relevance_threshold
        self.graph = self._build_graph()

    def _scope(self, state: State):
        q = state["question"].lower()
        terms = [
            "farmer", "farm", "agriculture", "agricultural", "crop", "scheme",
            "subsidy", "irrigation", "soil", "seed", "fertilizer", "fertiliser",
            "pest", "disease", "dairy", "livestock", "fisher", "fisheries",
            "horticulture", "beekeep", "kisan", "cultivation", "mandi", "market",
            "harvest", "paddy", "rice", "wheat", "cotton", "insurance", "pmfby",
            "pm kisan", "agri", "loan", "tractor", "farm infrastructure", "organic",
        ]
        in_scope = any(term in q for term in terms)
        return {
            "scope": "IN_SCOPE" if in_scope else "OUT_OF_SCOPE",
            "query": state["question"],
        }

    def _retrieve(self, state: State):
        try:
            pairs = self.vector_store.similarity_search_with_relevance_scores(
                state["query"], k=self.k
            )
            docs = [doc for doc, _score in pairs]
            scores = [float(score) for _doc, score in pairs]
            return {"documents": docs, "retrieval_scores": scores, "source_mode": "PDF"}
        except AttributeError:
            # Compatibility fallback for vector stores that do not expose scores.
            docs = self.vector_store.similarity_search(state["query"], k=self.k)
            return {
                "documents": docs,
                "retrieval_scores": [],
                "source_mode": "PDF",
            }
        except Exception as exc:
            raise RAGServiceError(
                "retrieval_error",
                "The agriculture knowledge base could not be accessed right now. Please try again later.",
                str(exc),
            ) from exc

    def _grade_documents(self, state: State):
        # Time-sensitive questions should use live web search instead of
        # relying on the static Vikaspedia PDF index.
        freshness_terms = [
        "latest",
        "recent",
        "new update",
        "updates",
        "announced",
        "announcement",
        "announcements",
        "current",
        "today",
        "this month",
        "this year",
        ]

        question = state["question"].lower().strip()

        has_year = any(str(year) in question for year in range(2024, 2031))
        asks_for_fresh_information = any(
        term in question for term in freshness_terms
        )

        if asks_for_fresh_information or has_year:
            return {"documents": []}
        """Local retrieval-confidence gate; deliberately no LLM call."""
        docs = state.get("documents", [])
        scores = state.get("retrieval_scores", [])

        if not docs:
            return {"documents": []}

        if not scores:
            return {"documents": docs[: self.k]}

        # FAISS relevance scores are expected to be higher for better matches.
        # If no PDF chunk reaches the confidence threshold, return no documents
        # so the graph can activate the web-search fallback.
        relevant = [
            doc for doc, score in zip(docs, scores)
            if score >= self.relevance_threshold
        ]
        
        return {"documents": relevant}

    @staticmethod
    def _format_history(history: list[dict[str, str]]) -> str:
        if not history:
            return "No previous conversation."
        lines = []
        for item in history[-8:]:
            role = item.get("role", "user").upper()
            lines.append(f"{role}: {item.get('content', '')}")
        return "\n".join(lines)

    @staticmethod
    def _format_pdf_context(docs: list[Document]) -> str:
        if not docs:
            return "No relevant PDF evidence was retrieved."
        parts = []
        for i, doc in enumerate(docs[:4], 1):
            source = doc.metadata.get("source_file", "unknown.pdf")
            page = doc.metadata.get("page")
            page_label = f", page {page}" if isinstance(page, int) else ""
            text = (doc.page_content or "")[:4500]
            parts.append(f"[PDF {i}: {source}{page_label}]\n{text}")
        return "\n\n".join(parts)

    @staticmethod
    def _format_web_context(results: list[dict[str, Any]]) -> str:
        if not results:
            return "No web evidence is available."
        parts = []
        for i, item in enumerate(results, 1):
            title = item.get("title", "Untitled")
            url = item.get("url", "")
            content = item.get("content", "")[:7000]
            parts.append(f"[WEB {i}] {title}\nURL: {url}\n{content}")
        return "\n\n".join(parts)

    def _generate(self, state: State):
        pdf_context = self._format_pdf_context(state.get("documents", []))
        web_context = self._format_web_context(state.get("web_results", []))
        context = f"{pdf_context}\n\nWEB EVIDENCE:\n{web_context}"

        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("system", GENERATION_PROMPT),
        ])
        messages = prompt.format_messages(
            context=context,
            history=self._format_history(state.get("history", [])),
            question=state["question"],
        )

        chunks = []
        try:
            for chunk in self.llm.stream(messages):
                content = getattr(chunk, "content", "")
                if content:
                    chunks.append(content)
        except Exception as exc:
            # Do not expose raw provider errors to the customer UI.
            # In particular, OpenAI 429/RPD responses can contain internal
            # organization details and URLs that are not customer-facing.
            raise _classify_llm_error(exc) from exc

        answer = "".join(chunks).strip()
        if not answer:
            raise RAGServiceError(
                "empty_response",
                "The adviser did not return an answer. Please try again later.",
                "LLM returned an empty response.",
            )

        source_mode = "PDF + Web" if state.get("web_used") else "PDF"
        sources: list[dict[str, str]] = []
        seen: set[str] = set()

        for doc in state.get("documents", []):
            filename = str(doc.metadata.get("source_file", "unknown.pdf"))
            page = doc.metadata.get("page")
            label = (
                f"PDF: {filename} — page {page}"
                if isinstance(page, int)
                else f"PDF: {filename}"
            )
            if label not in seen:
                sources.append({"type": "PDF", "label": label})
                seen.add(label)

        for item in state.get("web_results", []):
            title = str(item.get("title", "Web source"))
            url = str(item.get("url", ""))
            label = f"WEB: {title} — {url}" if url else f"WEB: {title}"
            if label not in seen:
                sources.append({"type": "WEB", "label": label})
                seen.add(label)

        return {
            "answer": answer,
            "source_mode": source_mode,
            "sources": sources,
        }

    def _grade_answer(self, state: State):
        # Lightweight mode: avoid another LLM call. The generation prompt is
        # the primary grounding control; evaluation is handled separately.
        return {
            "supported": True,
            "answers_question": True,
            "grade_reason": "Answer generated using the configured evidence policy.",
        }

    def _web_search(self, state: State):
        try:
            results = self.web_search.search(state.get("query") or state["question"])
            return {
                "web_results": results,
                "web_used": bool(results),
                "web_error": "" if results else "No web results returned.",
                "source_mode": "PDF + Web" if results else "PDF",
            }
        except Exception as exc:
            return {
                "web_results": [],
                "web_used": False,
                "web_error": str(exc),
                "source_mode": "PDF",
            }

    def _out_of_scope(self, state: State):
        return {
            "answer": (
                "I’m focused on agriculture and farmer-support questions. "
                "Please ask about crops, farming, irrigation, soil, livestock, fisheries, "
                "government schemes, subsidies, crop insurance, loans, or related topics."
            ),
            "source_mode": "No retrieval",
        }

    def _after_scope(self, state: State):
        return "retrieve" if state.get("scope") == "IN_SCOPE" else "out_of_scope"

    def _after_grade_docs(self, state: State):
        return "generate" if state.get("documents") else "web_search"

    def _after_answer_grade(self, state: State):
        return "end"

    def _build_graph(self):
        graph = StateGraph(State)
        graph.add_node("scope", self._scope)
        graph.add_node("retrieve", self._retrieve)
        graph.add_node("grade_documents", self._grade_documents)
        graph.add_node("web_search", self._web_search)
        graph.add_node("generate", self._generate)
        graph.add_node("grade_answer", self._grade_answer)
        graph.add_node("out_of_scope", self._out_of_scope)

        graph.add_edge(START, "scope")
        graph.add_conditional_edges("scope", self._after_scope, {
            "retrieve": "retrieve",
            "out_of_scope": "out_of_scope",
        })
        graph.add_edge("retrieve", "grade_documents")
        graph.add_conditional_edges("grade_documents", self._after_grade_docs, {
            "generate": "generate",
            "web_search": "web_search",
        })
        graph.add_edge("web_search", "generate")
        graph.add_edge("generate", "grade_answer")
        graph.add_conditional_edges("grade_answer", self._after_answer_grade, {"end": END})
        graph.add_edge("out_of_scope", END)
        return graph.compile()

    def stream(self, question: str, history: list[dict[str, str]] | None = None):
        initial: State = {
            "question": question,
            "query": question,
            "history": history or [],
            "retry_count": 0,
            "web_used": False,
            "documents": [],
            "web_results": [],
        }
        return self.graph.stream(
            initial,
            stream_mode=["messages", "updates"],
            version="v2",
        )
