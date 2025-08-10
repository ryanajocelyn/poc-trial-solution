import typing
from decimal import Decimal

from borb.pdf.canvas.geometry.rectangle import Rectangle
from borb.pdf.canvas.layout.annotation.text_annotation import TextAnnotation
from borb.pdf.document.document import Document
from borb.pdf.page.page import Page
from borb.pdf.pdf import PDF


# Load the existing PDF
def extract_text_from_pdf(file_path: str):
    # Read the PDF
    doc: typing.Optional[Document] = None
    with open(file_path, "rb") as pdf_file_handle:
        doc = PDF.loads(pdf_file_handle)

    if doc is None:
        raise ValueError("Failed to load PDF.")

    text_content = []
    for page in doc.get_pages():
        # Extract text from each page
        text = page.extract_text()
        text_content.append(text)

    return text_content


def add_annotation_to_pdf(
    input_pdf_path: str,
    output_pdf_path: str,
    page_number: int,
    x: float,
    y: float,
    width: float,
    height: float,
    content: str,
):
    doc: typing.Optional[Document] = None
    with open(input_pdf_path, "rb") as pdf_file_handle:
        doc = PDF.loads(pdf_file_handle)

    if doc is None:
        raise ValueError("Failed to load PDF.")

    pages = list(doc.get_pages())
    if page_number >= len(pages):
        raise IndexError("Page number out of range.")

    page: Page = pages[page_number]

    # Define the annotation rectangle
    annotation_rect = Rectangle(Decimal(x), Decimal(y), Decimal(width), Decimal(height))

    # Create a text annotation
    annotation = TextAnnotation(rectangle=annotation_rect, contents=content)

    # Add the annotation to the page
    page.add_annotation(annotation)

    # Save the modified PDF
    with open(output_pdf_path, "wb") as pdf_out:
        PDF.dumps(pdf_out, doc)


if __name__ == "__main__":
    input_pdf = "blank_crf.pdf"  # Your input PDF
    output_pdf = "borb_annotated_output.pdf"  # Output PDF with annotation

    # 1. Extract Text
    extracted_text = extract_text_from_pdf(input_pdf)
    print("Extracted Text from PDF:")
    for page_num, text in enumerate(extracted_text):
        print(f"Page {page_num+1}:")
        print(text)
        print("=" * 40)

    # 2. Add an annotation
    add_annotation_to_pdf(
        input_pdf_path=input_pdf,
        output_pdf_path=output_pdf,
        page_number=0,  # Annotate on first page
        x=Decimal(50),  # X position
        y=Decimal(600),  # Y position
        width=Decimal(100),
        height=Decimal(50),
        content="This is a sample annotation added via borb!",
    )

    print(f"Annotation added and saved to {output_pdf}")
