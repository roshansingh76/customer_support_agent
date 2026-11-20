from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader


class PdfLoaderManager:

    def __init__(self, directory: str = "../../../datadocs"):
        self.directory = directory


    def process_all_pdf(self):
        """Process all PDF files in the directory."""
        all_documents = []
        pdf_dir = Path(self.directory)

        try:
            if not pdf_dir.exists():
                print(f"PDF directory does not exist: {pdf_dir}")
                return all_documents

            pdf_files = list(pdf_dir.glob("**/*.pdf"))
        except OSError as exc:
            print(f"Could not access PDF directory {pdf_dir}: {exc}")
            return all_documents

        print(f"Found {len(pdf_files)} PDF files to process")

        for pdf_row in pdf_files:
            print(f"\nProcessing file: {pdf_row.name}\n")
            try:
                loader = PyPDFLoader(str(pdf_row))
                documents = loader.load()
                for doc in documents:
                    doc.metadata["source_file"] = pdf_row.name
                    doc.metadata["file_type"] = "pdf"

                all_documents.extend(documents)
                print(f"Loaded {len(documents)} pages")
            except Exception as exc:
                print(f"Could not process PDF {pdf_row}: {exc}")

        return all_documents















