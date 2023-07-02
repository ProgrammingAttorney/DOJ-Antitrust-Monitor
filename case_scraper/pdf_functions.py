# import requests
# import PyPDF2
# import regex as re
# from bs4 import BeautifulSoup
# from io import BytesIO
#
# # extract_pdf_content("https://www.justice.gov/atr/case-document/file/513946/download")
#
# import pytesseract
# from pdf2image import convert_from_bytes
#
# # Make sure to install pdf2image: pip install pdf2image
# # And also install poppler-utils: sudo apt-get install -y poppler-utils (for Ubuntu)
# # make sure to install poppler
#
# import fitz  # PyMuPDF
# def needs_ocr(pdf_file):
#     """
#     Determine whether a PDF file needs OCR (Optical Character Recognition).
#
#     :param pdf_file: Bytes Content of PDF File or path to the file.
#     :return: A boolean indicating whether the PDF file needs OCR.
#     """
#     if isinstance(pdf_file, str):
#         if pdf_file.startswith("http"):
#             response = requests.get(pdf_file)
#             pdf_content = response.content
#         else:
#             with open(pdf_file, "rb") as fp:
#                 pdf_content = fp.read()
#     elif isinstance(pdf_file, (bytes, bytearray)):
#         pdf_content = pdf_file
#     else:
#         raise TypeError('pdf_file must be a string representing a file path or a bytes-like object representing the content of a PDF file')
#
#     doc = fitz.open(stream=pdf_content, filetype="pdf")
#     text_threshold = 50
#     image_pages = sum(1 for page_num in range(len(doc)) if len(doc.load_page(page_num).get_text().strip()) < text_threshold)
#     return image_pages > len(doc) / 2
#
#
# def extract_pdf_content_ocr(pdf_file):
#     """
#     Perform OCR on pdf images.
#
#     :param pdf_file: Bytes Content of pdf File.
#     :return: A string containing the text extracted from the PDF file.
#     """
#     images = convert_from_bytes(pdf_file.read())
#     return "".join(pytesseract.image_to_string(image) for image in images)
#
#
#
# def pdf_to_text(file):
#     """
#     Convert a given PDF file to text.
#
#     :param file: A file-like object representing the PDF file.
#     :return: A string containing the extracted text.
#     """
#     reader = PyPDF2.PdfFileReader(file)
#     text = "".join(reader.getPage(page_num).extractText() for page_num in range(reader.numPages))
#     return text
# def download_pdf(url):
#     """
#     Download a PDF file from a given URL.
#
#     :param url: A string containing the URL of the PDF file.
#     :return: A file-like object representing the downloaded PDF file.
#     """
#     response = requests.get(url)
#     pdf_file = BytesIO(response.content)
#     return pdf_file
#
# def extract_text_from_pdf(pdf_url):
#
#
#     pdf_content = download_pdf(pdf_url)
#     if needs_ocr(pdf_content):
#         text = extract_pdf_content_ocr(pdf_content)
#     else:
#         doc = fitz.open(stream=pdf_content, filetype="pdf")
#         text = ""
#         for page_num in range(len(doc)):
#             page = doc.load_page(page_num)
#             text += page.get_text()
#
#
#
#     return text
#
# def get_document_date(pdf_url):
#     text = extract_text_from_pdf(pdf_url)
#     date_patterns = [r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b',
#                      r'\b\d{1,2}\/\d{1,2}\/\d{4}\b',
#                      r'\b\d{4}\-\d{1,2}\-\d{1,2}\b']
#     for pattern in date_patterns:
#         date_match = re.search(pattern, text)
#         if date_match:
#             return date_match.group(0)
#     return None
#
# def get_optimized_text(pdf_url):
#     text = extract_text_from_pdf(pdf_url)
#     # Add any additional text optimizations here
#     return text