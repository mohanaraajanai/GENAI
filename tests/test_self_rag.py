from rag.self_rag import SelfRAG


def make_rag():
    return SelfRAG(vector_store=object(), llm=object(), k=2)


def test_agriculture_question_is_in_scope():
    rag = make_rag()
    result = rag._scope({"question": "What is crop insurance?"})
    assert result["scope"] == "IN_SCOPE"


def test_non_agriculture_question_is_out_of_scope():
    rag = make_rag()
    result = rag._scope({"question": "Write a movie review"})
    assert result["scope"] == "OUT_OF_SCOPE"
