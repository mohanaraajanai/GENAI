from __future__ import annotations

from pathlib import Path

import pymupdf
import pytesseract
from dotenv import load_dotenv
from PIL import Image

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv()


class FAISSIndexer:

    def __init__(
        self,
        downloads_dir="downloads",
        index_dir="data/faiss_index",
    ):
        self.downloads_dir = Path(downloads_dir)
        self.index_dir = Path(index_dir)

    @property
    def embeddings(self):
        return OpenAIEmbeddings(
            model="text-embedding-3-small"
        )

    def extract_page_text(self, page, pdf_name, page_number):
        """
        Extract text from a PDF page.

        First tries normal PDF text extraction.
        If the extracted text is too small, OCR is used.
        """

        # -------------------------------------------------
        # STEP 1: Normal PDF text extraction
        # -------------------------------------------------

        text = page.get_text("text").strip()

        # Ignore useless extraction such as:
        # "vikaspedia.in"
        if len(text) >= 100:
            print(
                f"      Page {page_number + 1}: "
                f"PDF text ({len(text)} chars)"
            )

            return text

        # -------------------------------------------------
        # STEP 2: OCR
        # -------------------------------------------------

        print(
            f"      Page {page_number + 1}: "
            f"Running OCR..."
        )

        # Render page at 300 DPI approximately.
        # Matrix 2 gives good OCR quality while keeping
        # processing time reasonable.
        pixmap = page.get_pixmap(
            matrix=pymupdf.Matrix(2, 2),
            alpha=False
        )

        image = Image.frombytes(
            "RGB",
            [pixmap.width, pixmap.height],
            pixmap.samples
        )

        # OCR configuration
        ocr_text = pytesseract.image_to_string(
            image,
            lang="eng",
            config="--psm 6"
        ).strip()

        if ocr_text:
            print(
                f"      Page {page_number + 1}: "
                f"OCR ({len(ocr_text)} chars)"
            )
        else:
            print(
                f"      Page {page_number + 1}: "
                f"OCR returned no text"
            )

        return ocr_text

    def load_documents(self):

        pdf_files = sorted(
            self.downloads_dir.glob("*.pdf")
        )

        if not pdf_files:
            raise FileNotFoundError(
                f"No PDF files found in "
                f"{self.downloads_dir}"
            )

        print(
            f"Found {len(pdf_files)} PDF file(s).\n"
        )

        documents = []

        for pdf_path in pdf_files:

            print(f"Loading: {pdf_path.name}")

            pdf = pymupdf.open(pdf_path)

            for page_number, page in enumerate(pdf):

                text = self.extract_page_text(
                    page,
                    pdf_path.name,
                    page_number
                )

                # Ignore genuinely empty pages
                if not text:
                    continue

                documents.append(
                    Document(
                        page_content=text,
                        metadata={
                            "source_file": pdf_path.name,
                            "source_path": str(pdf_path),
                            "source_type": "Vikaspedia PDF",
                            "page": page_number + 1,
                        },
                    )
                )

            pdf.close()

        return documents

    def build(
        self,
        chunk_size=1000,
        chunk_overlap=150,
    ):

        print("=" * 70)
        print(" Vikaspedia RAG - FAISS Index Builder")
        print("=" * 70)

        print(f"\nChunk size    : {chunk_size}")
        print(f"Chunk overlap : {chunk_overlap}")
        print("Embedding     : text-embedding-3-small")
        print(f"PDF directory : {self.downloads_dir}")
        print(f"FAISS index   : {self.index_dir}")

        # -------------------------------------------------
        # STEP 1
        # -------------------------------------------------

        print("\nSTEP 1 - Loading PDF files")
        print("-" * 70)

        documents = self.load_documents()

        print(
            f"\nPDF pages/documents loaded : "
            f"{len(documents)}"
        )

        total_characters = sum(
            len(doc.page_content)
            for doc in documents
        )

        print(
            f"Total extracted characters : "
            f"{total_characters:,}"
        )

        # -------------------------------------------------
        # STEP 2 - Split text
        # -------------------------------------------------

        print("\nSTEP 2 - Splitting documents")
        print("-" * 70)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                "",
            ],
        )

        chunks = splitter.split_documents(
            documents
        )

        print(
            f"Chunks created : {len(chunks)}"
        )

        # -------------------------------------------------
        # STEP 3 - Embeddings
        # -------------------------------------------------

        print(
            "\nSTEP 3 - Creating OpenAI embeddings"
        )
        print("-" * 70)

        print(
            "Using model: "
            "text-embedding-3-small"
        )

        embeddings = self.embeddings

        # -------------------------------------------------
        # STEP 4 - FAISS
        # -------------------------------------------------

        print(
            "\nSTEP 4 - Building FAISS vector database"
        )
        print("-" * 70)

        vector_store = FAISS.from_documents(
            chunks,
            embeddings
        )

        # -------------------------------------------------
        # STEP 5 - Save
        # -------------------------------------------------

        print(
            "\nSTEP 5 - Saving FAISS index"
        )
        print("-" * 70)

        self.index_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        vector_store.save_local(
            str(self.index_dir)
        )

        print(
            "\nFAISS index saved successfully."
        )

        print("\n" + "=" * 70)
        print(" INDEXING COMPLETED SUCCESSFULLY")
        print("=" * 70)

        print(
            f"\nPDF pages/documents : "
            f"{len(documents)}"
        )

        print(
            f"Characters          : "
            f"{total_characters:,}"
        )

        print(
            f"Chunks              : "
            f"{len(chunks)}"
        )

        print(
            f"Chunk size          : "
            f"{chunk_size}"
        )

        print(
            f"Chunk overlap       : "
            f"{chunk_overlap}"
        )

        print(
            "Embedding model     : "
            "text-embedding-3-small"
        )

        print(
            f"FAISS directory     : "
            f"{self.index_dir}"
        )

        return vector_store

    def exists(self):

        return (
            (self.index_dir / "index.faiss").exists()
            and
            (self.index_dir / "index.pkl").exists()
        )

    def load(self):

        if not self.exists():
            raise FileNotFoundError(
                "FAISS index does not exist. "
                "Run the index builder first."
            )

        return FAISS.load_local(
            str(self.index_dir),
            self.embeddings,
            allow_dangerous_deserialization=True,
        )


def main():

    indexer = FAISSIndexer()

    indexer.build(
        chunk_size=1000,
        chunk_overlap=150,
    )


if __name__ == "__main__":
    main()