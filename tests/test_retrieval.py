from rag.indexer import FAISSIndexer


def main():

    print("=" * 70)
    print(" VIKASPEDIA RAG - RETRIEVAL TEST")
    print("=" * 70)

    indexer = FAISSIndexer()

    print("\nLoading FAISS index...")
    vector_store = indexer.load()

    questions = [
        "What is Pradhan Mantri Fasal Bima Yojana?",
        "What benefits are available under crop insurance schemes?",
        "What is Agriculture Infrastructure Fund?",
        "What is PM Kisan Samman Nidhi?",
    ]

    for question in questions:

        print("\n" + "=" * 70)
        print("QUESTION")
        print("=" * 70)
        print(question)

        results = vector_store.similarity_search(
            question,
            k=3
        )

        print("\nTOP RETRIEVED DOCUMENTS")
        print("-" * 70)

        for i, doc in enumerate(results, start=1):

            print(f"\n[{i}]")

            print(
                "Source:",
                doc.metadata.get("source_file")
            )

            print(
                "Page:",
                doc.metadata.get("page")
            )

            print(
                "\n",
                doc.page_content[:1200]
            )

    print("\n" + "=" * 70)
    print(" RETRIEVAL TEST COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()