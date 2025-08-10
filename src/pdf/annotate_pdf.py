import fitz  # PyMuPDF


def annotate_pdf_free_text(
    input_pdf_path,
    output_pdf_path,
    page_number,
    text_content,
    x1,
    y1,
    x2,
    y2,
    font_size=10,
    font_name="helv",
    border_color=(0, 0, 0),
    background_color=(0, 1, 0),
):
    """
    Annotates a PDF with free text with a black border and green background.

    Args:
        input_pdf_path (str): Path to the input PDF file.
        output_pdf_path (str): Path to save the annotated PDF file.
        page_number (int): The 0-indexed page number to annotate.
        text_content (str): The text content of the annotation.
        x1 (float): X-coordinate of the top-left corner of the annotation rectangle.
        y1 (float): Y-coordinate of the top-left corner of the annotation rectangle.
        x2 (float): X-coordinate of the bottom-right corner of the annotation rectangle.
        y2 (float): Y-coordinate of the bottom-right corner of the annotation rectangle.
        font_size (float): Font size of the text.
        font_name (str): Font name (e.g., "helv", "cour", "times", "symb").
        border_color (tuple): RGB tuple for the border color (0-1). Default is black.
        background_color (tuple): RGB tuple for the background color (0-1). Default is green.
    """
    try:
        doc = fitz.open(input_pdf_path)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return

    if page_number < 0 or page_number >= len(doc):
        print(f"Error: Page number {page_number} is out of range for this document.")
        doc.close()
        return

    page = doc[page_number]

    # Define the rectangle for the annotation
    rect = fitz.Rect(x1, y1, x2, y2)

    # Create the text annotation
    annot = page.add_freetext_annot(
        rect,
        text_content,
        fill_color=background_color,  # Background color
        text_color=border_color,  # Text color (can be different from border)
        fontname=font_name,
        fontsize=font_size,
    )

    # Set the border color and width
    # PyMuPDF uses the 'colors' parameter for border color
    # and 'border' parameter for border width and dash pattern
    # annot.set_colors(stroke=border_color, fill=background_color)
    annot.set_border(width=1)  # Set border width to 1 (can be adjusted)

    try:
        doc.save(output_pdf_path)
        print(f"PDF annotated successfully and saved to {output_pdf_path}")
    except Exception as e:
        print(f"Error saving annotated PDF: {e}")
    finally:
        doc.close()


if __name__ == "__main__":
    # Create a dummy PDF for demonstration
    pdf_path = "D:\\Abiz\\Technical\\code\\python\\poc-trial-solution\\src\pdf\\blan_crf_sample.pdf"
    output_pdf_path = "D:\\Abiz\\Technical\\code\\python\\poc-trial-solution\\src\pdf\\annotated_output.pdf"

    # Example usage: Annotate the first page (page_number=0)
    # The rectangle defines where the annotation box will appear
    annotate_pdf_free_text(
        input_pdf_path=pdf_path,
        output_pdf_path=output_pdf_path,
        page_number=0,
        text_content="This is a free text annotation with black border and green background!",
        x1=100,
        y1=100,
        x2=400,
        y2=150,  # Coordinates for the annotation box
        font_size=12,
        font_name="helv",
        border_color=(0, 0, 0),  # Black border (RGB)
        background_color=(0, 1, 0),  # Green background (RGB)
    )

    print("\nPlease open 'annotated_output.pdf' to see the annotation.")
