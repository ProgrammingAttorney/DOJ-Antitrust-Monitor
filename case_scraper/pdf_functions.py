import requests
import PyPDF2
import regex as re
from bs4 import BeautifulSoup
from io import BytesIO




def extract_pdf_content(pdf_url):
    response = requests.get(pdf_url)
    pdf_file = BytesIO(response.content)
    reader = PyPDF2.PdfFileReader(pdf_file)
    text = ""
    for page_num in range(reader.numPages):
        page = reader.getPage(page_num)
        text += page.extractText()
    return text

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
    response = requests.get(pdf_url)
    pdf_content = BytesIO(response.content)
    pdf_reader = PyPDF2.PdfFileReader(pdf_content)
    text = ""
    for page in range(pdf_reader.getNumPages()):
        text += pdf_reader.getPage(page).extractText()
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