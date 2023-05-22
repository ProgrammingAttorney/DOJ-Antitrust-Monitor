import requests
import PyPDF2
import regex as re
from bs4 import BeautifulSoup
from io import BytesIO

# extract_pdf_content("https://www.justice.gov/atr/case-document/file/513946/download")

import pytesseract
from pdf2image import convert_from_bytes

# Make sure to install pdf2image: pip install pdf2image
# And also install poppler-utils: sudo apt-get install -y poppler-utils (for Ubuntu)
# make sure to install poppler


import fitz  # PyMuPDF

def needs_ocr(pdf_file):
    """
    :param pdf_file: Bytes Content of PDF File or path to the file
    :return:
    """
    
    if isinstance(pdf_file, str):
        # If a filepath is given
        with open(pdf_file, "rb") as fp:
            pdf_content = fp.read()
        doc = fitz.open(stream=pdf_content, filetype="pdf")
    elif isinstance(pdf_file, (bytes, bytearray)):
        # If a bytes-like object is given
        doc = fitz.open(stream=pdf_file, filetype="pdf")
    else:
        raise TypeError('pdf_file must be a string representing a file path or a bytes-like object representing the content of a PDF file')
    
    text_threshold = 50  # Minimum number of non-whitespace characters to consider a page as text-based
    image_pages = 0
    text_pages = 0
    
    for page_num in range(len(doc)):
        
        page = doc.load_page(page_num)
        text = page.get_text()
        
        # Count non-whitespace characters
        non_whitespace_chars = sum(1 for char in text if not char.isspace())
        
        if non_whitespace_chars < text_threshold:
            image_pages += 1
        else:
            text_pages += 1
    
    # If the majority of pages are image-based or have little text content, the PDF might need OCR
    if image_pages > text_pages:
        return True
    else:
        return False

def extract_pdf_content_ocr(pdf_file):
    """
    Function designed to perform OCR on pdf images. This needs pytesseract, tesseract, and poppler to be installed.
    :param pdf_file: Bytes Content of pdf File
    :return:
    """
    # Convert PDF pages to images
    images = convert_from_bytes(pdf_file.read())
    
    # Perform OCR on the images using pytesseract
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image)
        # print(text)
    
    return text

# def extract_pdf_content(pdf_url):
#     response = requests.get(pdf_url)
#     pdf_file = BytesIO(response.content)
#     reader = PyPDF2.PdfFileReader(pdf_file)
#     text = ""
#     for page_num in range(reader.numPages):
#         page = reader.getPage(page_num)
#         text += page.extractText()
#         print(text)
#     return text

def pdf_to_text(file):
    """
    Convert a given PDF file to text.
    :param file: A file-like object representing the PDF file.
    :return: A string containing the extracted text.
    """
    reader = PyPDF2.PdfFileReader(file)
    text = ""

    for page_num in range(reader.numPages):
        text += reader.getPage(page_num).extractText()

    return text

def download_pdf(url):
    """
    Download a PDF file from a given URL.
    :param url: A string containing the URL of the PDF file.
    :return: A file-like object representing the downloaded PDF file.
    """
    response = requests.get(url)
    pdf_file = BytesIO(response.content)

    return pdf_file

def extract_text_from_pdf(pdf_url):


    pdf_content = download_pdf(pdf_url)
    if needs_ocr(pdf_content):
        text = extract_pdf_content_ocr(pdf_content)
    else:
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()



    return text

def get_document_date(pdf_url):
    text = extract_text_from_pdf(pdf_url)
    date_patterns = [r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b',
                     r'\b\d{1,2}\/\d{1,2}\/\d{4}\b',
                     r'\b\d{4}\-\d{1,2}\-\d{1,2}\b']
    for pattern in date_patterns:
        date_match = re.search(pattern, text)
        if date_match:
            return date_match.group(0)
    return None

def get_optimized_text(pdf_url):
    text = extract_text_from_pdf(pdf_url)
    # Add any additional text optimizations here
    return text