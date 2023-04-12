import datetime
import re
import requests
import urllib
from .pdf_functions import  extract_pdf_content
from bs4 import BeautifulSoup




BASE_URL = "https://www.justice.gov/"


def collect_HTML_tables():
    case_list = []
    # Create a session object for HTTP requests
    with requests.Session() as session:
        # Use a generator expression to iterate over the page numbers
        urls = (f"https://www.justice.gov/atr/antitrust-case-filings?f%5B0%5D=field_case_type%3Acivil_merger&page={i}" for i in range(0, 23))
        # Use a list comprehension to extract the table rows
        case_list = [row for url in urls for row in BeautifulSoup(session.get(url).text, "html.parser").find_all("tr")]
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

def extract_case_data(case_row):
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
    case_type = "".join([el.find('span').text for el in type_elements])
    
    # Extract federal court
    federal_court = "".join([el.find('span').text for el in federal_court_elements])
    
    # Extract industry
    industry = "".join([el.find('span').text for el in industry_elements])
    
    # Convert case open date to a datetime object
    date_format = "%A, %B %d, %Y"
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

def get_document_details(doc_page_link):
    """
    Given a URL of a document page, this function extracts details such as
    the document date, document type, and any other relevant information.

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
    result = {}

    # Iterate through the pairs of field labels and field items
    for label, items in zip(field_labels, field_items):
        key = label.get_text(strip=True).lower().strip()
        
        # Check if the field item contains a link
        if items.find('a', href=True):
            links = items.find_all('a', href=True)
            values = [{'text': link.get_text(strip=True), 'url': urllib.parse.urljoin(BASE_URL, link['href'])} for link in links if link['href'].endswith("pdf")]
        else:
            values = [item.get_text(strip=True) for item in items]

        # Check if the value is a date in the given format
        if key.lower() == 'date':
            date_str = values[0]
            date_format = "%A, %B %d, %Y"
            date_obj = datetime.datetime.strptime(date_str, date_format)
            result['date object'] = date_obj
        else:
            result[key] = values
    result["content"] = extract_pdf_content()

    return result


def extract_case_details(case_link):
    """
    Given a URL of a case page, this function extracts details such as
    the markets, violation, and documents.


    :param case_link: str, URL of the case page
    :return: dict, a dictionary containing extracted details from the document page
    """
    markets = ""
    violation = ""
    documents = []
    base_url = "https://www.justice.gov/"
    page = requests.get(case_link)
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


def extract_case_information(case_link):

    case_link = urllib.parse.urljoin("https://www.justice.gov/", case_link)
    response = requests.get(case_link)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract case details
    open_date = soup.find('td', {'class': 'views-field views-field-field-case-date'}).text.strip()
    case_date = datetime.datetime.strptime(open_date, "Open Date: %B %d, %Y").strftime('%B %d, %Y')

    case_details = {
            "case_title": case_title,
            "case_link": case_link,
            "case_open_date": case_open_date,
            "case_type": case_type,
            "federal_court": federal_court,
            "industry": industry
        }
    return case_details

    # Extract case documents
    documents = []
    docs_table = soup.find('table', {'id': 'documents'})
    if docs_table:
        rows = docs_table.find_all('tr')
        for row in rows[1:]:
            cells = row.find_all('td')
            doc_link = cells[0].find('a')['href']
            doc_date = get_document_date(doc_link)
            doc_date_obj = datetime.datetime.strptime(doc_date, '%B %d, %Y') if doc_date else None
            documents.append({
                "docTitle": cells[0].text.strip(),
                "docLink": doc_link,
                "docDate": doc_date,
                "docDateObj": doc_date_obj
            })
    case_details["documents"] = documents

    return case_details

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

