import datetime
import re
import requests
import urllib
from .pdf_functions import  extract_text_from_pdf
from.utilities import is_pdf_link
from bs4 import BeautifulSoup
import pdb
#Scraper is tailored to only extract merger cases



BASE_URL = "https://www.justice.gov/"


def collect_HTML_tables():
    """
    Function to go through the DOJ's civil merger cases dating back to 200 and extract the tr tags from the website.
    Each TR Tag represents a case
    :return: list, a list of tr tags, with each tag representing a case
    """

    # Create a session object for HTTP requests
    with requests.Session() as session:
        # Use a generator expression to iterate over the page numbers
        urls = (f"https://www.justice.gov/atr/antitrust-case-filings?f%5B0%5D=field_case_type%3Acivil_merger&page={i}" for i in range(0, 23))
        # Use a list comprehension to extract the table rows
        case_list = [row for url in urls for row in BeautifulSoup(session.get(url).text, "html.parser").find_all("tr")[1:]]
    return case_list

# def extract_case_data(case_row):
#     """
#     This function extracts various case details from a single row of case data.
#
#     :param case_row: BeautifulSoup Tag
#     :return: dict,  a dictionary containing the extracted case details.
#     """
#     # Initialize empty strings for the case details
#     case_title = ""
#     case_link = ""
#     case_open_date = ""
#     case_type = ""
#     federal_court = ""
#     industry = ""
#
#     # Find the relevant HTML elements for each case detail
#     case_title_elements = case_row.find_all('td', {'class': 'views-field views-field-title'})
#     date_elements = case_row.find_all('td', {'class': 'views-field views-field-field-case-date'})
#     type_elements = case_row.find_all('td', {'class': 'views-field views-field-field-case-type'})
#     federal_court_elements = case_row.find_all('td', {'class': 'views-field views-field-field-brief-federal-court'})
#     industry_elements = case_row.find_all('td', {'class': 'views-field views-field-field-case-industry'})
#
#     # Extract case title and link
#     for el in case_title_elements:
#         a_el = el.find('a')
#         case_title += a_el.text + " "
#         case_href = a_el.get("href")
#         case_link = urllib.parse.urljoin(BASE_URL, case_href)
#         break
#
#     # Extract case open date
#     for el in date_elements:
#         span_el = el.find('span')
#         case_open_date += span_el.text
#
#     # Extract case type
#     for el in type_elements:
#         span_el = el.find('span')
#         case_type += span_el.text
#
#     # Extract federal court
#     for el in federal_court_elements:
#         span_el = el.find('span')
#         federal_court += span_el.text
#
#     # Extract industry
#     for el in industry_elements:
#         span_el = el.find('span')
#         industry += span_el.text
#
#     # Convert case open date to a datetime object
#     date_format = "%A, %B %d, %Y"
#     date_obj = datetime.datetime.strptime(case_open_date, date_format)
#
#     # Return the extracted case details as a dictionary
#     return {
#             "case_title": case_title,
#             "case_link": case_link,
#             "case_open_date": case_open_date,
#             "case_open_date_obj": date_obj,
#             "case_type": case_type,
#             "federal_court": federal_court,
#             "industry": industry
#             }

def extract_case_data_from_row(case_row):
    """
    This function extracts various case details from a single row of case data.
    
    :param case_row: BeautifulSoup Tag
    :return: dict,  a dictionary containing the extracted case details.
    """
    # Find the relevant HTML elements for each case detail
    case_title_elements = case_row.find_all('td', {'class': 'views-field views-field-title'})
    date_elements = case_row.find_all('td', {'class': 'views-field views-field-field-case-date'})
    type_elements = case_row.find_all('td', {'class': 'views-field views-field-field-case-type'})
    federal_court_elements = case_row.find_all('td', {'class': 'views-field views-field-field-brief-federal-court'})
    industry_elements = case_row.find_all('td', {'class': 'views-field views-field-field-case-industry'})
    
    # Extract case title and link
    case_title = " ".join([el.find('a').text for el in case_title_elements])
    case_href = case_title_elements[0].find('a').get("href")
    case_link = urllib.parse.urljoin(BASE_URL, case_href)
    
    # Extract case open date
    case_open_date = "".join([el.find('span').text for el in date_elements])
    
    # Extract case type
    case_type = "".join([el.get_text(strip=True) for el in type_elements])
    
    # Extract federal court
    federal_court = "".join([el.get_text(strip=True) for el in federal_court_elements])
    
    # Extract industry
    industry = "".join([el.get_text(strip=True) for el in industry_elements])
    
    # Convert case open date to a datetime object
    date_format = "%B %d, %Y"
    date_obj = datetime.datetime.strptime(case_open_date, date_format)
    
    # Return the extracted case details as a dictionary
    return {
            "case_title": case_title,
            "case_link": case_link,
            "case_open_date": case_open_date,
            "case_open_date_obj": date_obj,
            "case_type": case_type,
            "federal_court": federal_court,
            "industry": industry
            }


def extract_case_details_from_casepage(casepage_link):
    """
    Given a URL of a case page, this function extracts details such as
    the markets, violation, and documents.


    :param casepage_link: str, URL of the case page
    :return: dict, a dictionary containing extracted details from the document page
    """
    markets = ""
    violation = ""
    documents = []
    base_url = "https://www.justice.gov/"
    page = requests.get(casepage_link)
    soup = BeautifulSoup(page.content, "html.parser")
    market_elements = soup.find_all('div', {'class': 'field field--name-field-case-market field--type-text field--label-above'})
    violation_elements = soup.find_all('div', {'class': 'field field--name-field-case-violation field--type-taxonomy-term-reference field--label-above'})
    document_elements = soup.find_all('div', {'class': 'field field--name-field-case-documents field--type-entityreference field--label-above'})

    for el in market_elements:
        item_el = el.find("div", {"class":"field__items"})
        markets += item_el.get_text(strip=True)

    for el in violation_elements:
        item_el = el.find("div", {"class":"field__items"})
        violation += item_el.get_text(strip=True)

    for el in document_elements:
        doc_els = el.find_all("div", {"class":"field__item"})
        for doc_el in doc_els:
            doc_name = doc_el.get_text(strip=True)
            doc_href = doc_el.a.get("href")
            doc_link = urllib.parse.urljoin(base_url, doc_href)
            doc_tup = (doc_name, doc_link)
            documents.append(doc_tup)

    return {"markets": markets,
        "violation": violation,
        "documents": documents}


def get_document_details_from_document_page(doc_page_link):
    """
    Given a URL of a document page, this function extracts details such as
    the document date, document type, and any other relevant information.
    Note: You can only use this function to extract details from a document page, but not a case page.
    :param doc_page_link: str, URL of the document page
    :return: dict, a dictionary containing extracted details from the document page
    """

    # Initialize variables to store document date and type
    document_date = ""
    document_type = ""

    # Fetch the content of the document page
    response = requests.get(doc_page_link)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find field labels and items on the page
    field_labels = soup.select('div.field__label')[1:]
    field_items = soup.select('div.field__items')

    # Initialize a dictionary to store the results
    result = {"title":""}

    # Iterate through the pairs of field labels and field items
    for label, items in zip(field_labels, field_items):
        key = label.get_text(strip=True).lower().strip().strip(":")

        # Check if the field item contains a link
        if items.find('a', href=True):
            links = items.find_all('a', href=True)
            values = [{'document': link.get_text(strip=True).strip("download ").strip("Download "), 'url': urllib.parse.urljoin(BASE_URL, link['href'])} for link
                      in links if is_pdf_link(urllib.parse.urljoin(BASE_URL, link['href']))]
        else:
            values = [item.get_text(strip=True) for item in items]

        # Check if the value is a date in the given format
        if key.lower() == 'date':

            date_str = values[0]
            date_format = "%A, %B %d, %Y"
            date_obj = datetime.datetime.strptime(date_str, date_format)
            result['date object'] = date_obj
            result[key] = values
        else:
            result[key] = values
    # Check if "attachments" key has more than one item
    if len(result.get("attachments", [])) > 0:
        # Iterate through the list of attachments
        for attachment in result["attachments"]:
            # Get the value from the "url" key
            url = attachment["url"]

            # Extract text from the PDF
            document_text = extract_text_from_pdf(url)

            # Store the document text in the subdictionary
            attachment["text"] = document_text
            # pdb.set_trace()
            doc_type = result["document type"][0]
            if "complaint" in doc_type.lower():
                result["title"] = "complaint"
            else:
                result["title"] = attachment['document']

    # result["content"] = extract_text_from_pdf()

    return result

def find_document_dates(case_link):
    response = requests.get(case_link)
    soup = BeautifulSoup(response.text, "html.parser")
    doc_list = soup.find_all("div", class_="views-row")
    return doc_list

def get_document_date(doc):
    date_str = doc.find("div", class_="views-field-field-filed-date").get_text(strip=True)
    date_obj = datetime.datetime.strptime(date_str, "%m/%d/%Y")
    return date_obj

def remove_extra_whitespace(string):
    return re.sub(r'\s+', ' ', string).strip()

def unpack_column_dict(column):
    result = []
    for item in column:
        line = []
        for key, value in item.items():
            line.append(f"{key}: {value}")
        result.append(" | ".join(line))
    return "\n".join(result)

def sort_documents(doc_list):
    result = []
    for doc in doc_list:
        title = remove_extra_whitespace(doc.find("div", class_="views-field-title").get_text(strip=True))
        link = doc.find("a", class_="pdf-link")["href"]
        date_obj = get_document_date(doc)
        result.append({"docTitle": title, "docLink": link, "docDateObj": date_obj})
    return sorted(result, key=lambda k: k["docDateObj"])

