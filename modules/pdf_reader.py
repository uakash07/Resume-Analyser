import fitz  # import PyMuPDF library (aliased as fitz) for PDF processing
def extract_text(pdf_file) -> str:  # define function that takes a PDF file object and returns extracted text as string
    """Extract all text content from a PDF file."""  # docstring explaining function purpose
    pdf_bytes = pdf_file.read()  # read the raw bytes from the uploaded file object
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")  # open the PDF from bytes stream using PyMuPDF
    full_text = ""  # initialize an empty string to accumulate all extracted text
    for page_num in range(len(doc)):  # loop through every page index in the PDF document
        page = doc.load_page(page_num)  # load the current page object from the document
        page_text = page.get_text()  # extract all text content from the current page
        full_text += page_text + "\n"  # append extracted page text plus newline to the accumulator
    doc.close()  # close the PDF document to free memory resources
    return full_text.strip()  # return the combined text with leading/trailing whitespace removed
