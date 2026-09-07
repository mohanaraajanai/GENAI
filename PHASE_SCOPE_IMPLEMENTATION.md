# Production Scope Implementation — RAG / Evidence / Evaluation / LangSmith

This patch advances the frozen scope:

- 5 Self-RAG quality
- 6 Low-request optimization
- 11 PDF source citations
- 12 Web fallback
- 14 Error-safe web/LLM flow
- 15 Evaluation framework
- 16 LangSmith observability

## Changed files

- `rag/self_rag.py` — local retrieval-confidence gate, PDF/web sources, safe web fallback, no per-document/answer LLM graders.
- `rag/web_search.py` — normalized Tavily fallback.
- `rag/llm.py` — LangSmith tags/metadata on the generation model.
- `evals/evaluation_dataset.json` — expanded evaluation cases with expected scope/source.
- `evals/evaluate.py` — retrieval-only and answer evaluation runner with pass-rate output.
- `tests/test_self_rag.py` — basic scope-routing tests.

## Run retrieval evaluation without consuming LLM generation requests

```cmd
python -m evals.evaluate --retrieval-only
```

This uses the existing FAISS index and does not call the chat LLM. It is the preferred first test.

## Run full answer evaluation

Only run this after the OpenAI rate-limit/quota issue is resolved because it makes generation requests:

```cmd
python -m evals.evaluate
```

Optionally:

```cmd
python -m evals.evaluate --model gpt-4.1-mini
```

## LangSmith

Set these in `.env`:

```text
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your-key
LANGSMITH_PROJECT=vikaspedia-agri-farmer-adviser
```

The application already uses LangChain/LangGraph, so LangSmith can trace the run when these variables are enabled. The LLM is additionally tagged with `agri-farmer-adviser` and `rag-generation`.

## Important

Do not rebuild the FAISS index just for this patch. The existing index remains compatible.
