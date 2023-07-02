import requests
import urllib
import datetime
import regex as re
from bs4 import BeautifulSoup
from .utilities import is_pdf_link

class CaseScraper:
    """
    A class used to scrape case data from the Department of Justice website.

    ...

    Attributes
    ----------
    BASE_URL : str
        The base URL for the Department of Justice website.
    start_page : int
        The first page to scrape.
    end_page : int
        The last page to scrape.

    Methods
    -------
    collect_HTML_tables():
        Collects HTML tables from the Department of Justice website.
    extract_case_data_from_row(case_row, details=["title", "date", "type", "federal_court", "industry"]):
        Extracts case data from a row of an HTML table.
    extract_case_details_from_casepage(casepage_link, details=["markets", "violation", "documents"]):
        Extracts case details from a case page.
    get_document_details_from_document_page(doc_page_link, details=["date", "type", "attachments"]):
        Gets document details from a document page.
    find_document_dates(case_link):
        Finds the dates of documents associated with a case.
    get_document_date(doc):
        Gets the date of a document.
    remove_extra_whitespace(string):
        Removes extra whitespace from a string.
    unpack_column_dict(column):
        Unpacks a column of a DataFrame that contains dictionaries.
    sort_documents(doc_list):
        Sorts a list of documents by date.
    """
    
    BASE_URL = "https://www.justice.gov/"
    
    def __init__(self, start_page=0, end_page=23):
        """
        Constructs all the necessary attributes for the CaseScraper object.

        Parameters
        ----------
            start_page : int, optional
                The first page to scrape (default is 0).
            end_page : int, optional
                The last page to scrape (default is 23).
        """
        
        self.start_page = start_page
        self.end_page = end_page
    
    def collect_HTML_tables(self):
        """
        Collects HTML tables from the Department of Justice website.

        Returns
        -------
        list
            A list of BeautifulSoup Tag objects representing the rows of the HTML tables.
        """
        
        case_list = []
        with requests.Session() as session:
            for i in range(self.start_page, self.end_page):
                url = f"https://www.justice.gov/atr/antitrust-case-filings?f%5B0%5D=field_case_type%3Acivil_merger&page={i}"
                try:
                    response = session.get(url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, "html.parser")
                    case_list.extend(soup.find_all("tr")[1:])
                except requests.HTTPError as e:
                    print(f"Unable to fetch data from {url}. Error: {e}")
        return case_list
    
    @staticmethod
    def extract_case_data_from_row(case_row, details=["title", "date", "type", "federal_court", "industry"]):
        """
        Extracts case data from a row of an HTML table.

        Parameters
        ----------
        case_row : bs4.element.Tag
            A BeautifulSoup Tag object representing a row of an HTML table.
        details : list, optional
            A list of strings representing the details to extract (default is ["title", "date", "type", "federal_court", "industry"]).

        Returns
        -------
        dict
            A dictionary containing the extracted case data.
        """
        
        case_data = {}
        try:
            if "title" in details:
            
                title_element = case_row.find_all('td', {'class': 'views-field views-field-title'})
                case_data["case_title"] = " ".join([el.find('a').text.strip() for el in title_element])
                case_data["case_link"] = urllib.parse.urljoin(CaseScraper.BASE_URL, title_element[0].find('a').get("href"))
            if "date" in details:
                date_element = case_row.find_all('td', {'class': 'views-field views-field-field-case-date'})
                case_data["case_open_date"] = " ".join([el.find('span').text.strip() for el in date_element])
                date_format = "%B %d, %Y"
                case_data["case_open_date_obj"] = datetime.datetime.strptime(case_data["case_open_date"], date_format)
            if "type" in details:
                type_element = case_row.find_all('td', {'class': 'views-field views-field-field-case-type'})
                case_data["case_type"] = " ".join([el.find('span').text.strip() for el in type_element])
            if "federal_court" in details:
                court_element = case_row.find_all('td', {'class': 'views-field views-field-field-brief-federal-court'})
                case_data["federal_court"] = " ".join([el.find('span').text.strip() for el in court_element])
            if "industry" in details:
                industry_element = case_row.find_all('td', {'class': 'views-field views-field-field-case-industry'})
                case_data["industry"] = " ".join([el.find('span').text.strip() for el in industry_element])
        except Exception as e:
            print(f"Error extracting case data: {e}")
        return case_data
    
    @staticmethod
    def extract_case_details_from_casepage(casepage_link, details=["markets", "violation", "documents"]):
        """
        Extracts case details from a case page.
    
        Parameters
        ----------
        casepage_link : str
            The URL of the case page.
        details : list, optional
            A list of strings representing the details to extract (default is ["markets", "violation", "documents"]).
    
        Returns
        -------
        dict
            A dictionary containing the extracted case details.
        """
        
        case_details = {}
        try:
            response = requests.get(casepage_link)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            if "markets" in details:
                market_element = soup.find_all('div', {'class': 'field field--name-field-case-market field--type-text field--label-above'})
                case_details["markets"] = " ".join([el.find("div", {"class":"field__items"}).get_text(strip=True) for el in market_element])
            if "violation" in details:
                violation_element = soup.find_all('div', {'class': 'field field--name-field-case-violation field--type-taxonomy-term-reference field--label-above'})
                case_details["violation"] = " ".join([el.find("div", {"class":"field__items"}).get_text(strip=True) for el in violation_element])
            if "documents" in details:
                document_elements = soup.find_all('div', {'class': 'field field--name-field-case-documents field--type-entityreference field--label-above'})
                case_details["documents"] = [{"doc_name": doc_el.get_text(strip=True), "doc_link": urllib.parse.urljoin(CaseScraper.BASE_URL, doc_el.a.get("href"))} for doc_el in document_elements]
        except requests.HTTPError as e:
            print(f"Unable to fetch data from {casepage_link}. Error: {e}")
        return case_details
    
    @staticmethod
    def get_document_details_from_document_page(doc_page_link, details=["date", "type", "attachments"]):
        """
        Gets document details from a document page.
    
        Parameters
        ----------
        doc_page_link : str
            The URL of the document page.
        details : list, optional
            A list of strings representing the details to extract (default is ["date", "type", "attachments"]).
    
        Returns
        -------
        dict
            A dictionary containing the extracted document details.
        """
        
        doc_details = {}
        try:
            response = requests.get(doc_page_link)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            field_labels = soup.select('div.field__label')[1:]
            field_items = soup.select('div.field__items')
            for label, items in zip(field_labels, field_items):
                key = label.get_text(strip=True).lower().strip().strip(":")
                if key in details:
                    if items.find('a', href=True):
                        links = items.find_all('a', href=True)
                        doc_details[key] = [{'document': link.get_text(strip=True).strip("download ").strip("Download "), 'url': urllib.parse.urljoin(CaseScraper.BASE_URL, link['href'])} for link in links if is_pdf_link(urllib.parse.urljoin(CaseScraper.BASE_URL, link['href']))]
                    else:
                        doc_details[key] = [item.get_text(strip=True) for item in items]
                    if key.lower() == 'date':
                        date_str = doc_details[key][0]
                        date_format = "%A, %B %d, %Y"
                        doc_details['date object'] = datetime.datetime.strptime(date_str, date_format)
        except requests.HTTPError as e:
            print(f"Unable to fetch data from {doc_page_link}. Error: {e}")
        return doc_details
    
    @staticmethod
    def find_document_dates(case_link):
        """
        Finds the dates of documents associated with a case.
    
        Parameters
        ----------
        case_link : str
            The URL of the case.
    
        Returns
        -------
        list
            A list of BeautifulSoup Tag objects representing the documents associated with the case.
        """
        
        try:
            response = requests.get(case_link)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            return soup.find_all("div", class_="views-row")
        except requests.HTTPError as e:
            print(f"Unable to fetch data from {case_link}. Error: {e}")
            return []
    
    @staticmethod
    def get_document_date(doc):
        """
        Gets the date of a document.
    
        Parameters
        ----------
        doc : bs4.element.Tag
            A BeautifulSoup Tag object representing a document.
    
        Returns
        -------
        datetime.datetime
            A datetime object representing the date of the document.
        """
        
        try:
            date_str = doc.find("div", class_="views-field-field-filed-date").get_text(strip=True)
            return datetime.datetime.strptime(date_str, "%m/%d/%Y")
        except Exception as e:
            print(f"Error extracting document date: {e}")
            return None
    
    @staticmethod
    def remove_extra_whitespace(string):
        """
        Removes extra whitespace from a string.
    
        Parameters
        ----------
        string : str
            The string to remove extra whitespace from.
    
        Returns
        -------
        str
            The string with extra whitespace removed.
        """
        
        return re.sub(r'\s+', ' ', string).strip()

    
    @staticmethod
    def unpack_column_dict(column):
        """
        Unpacks a column of a DataFrame that contains dictionaries.
    
        Parameters
        ----------
        column : pandas.Series
            A column of a DataFrame that contains dictionaries.
    
        Returns
        -------
        str
            A string representing the unpacked column.
        """
        
        result = []
        for item in column:
            line = []
            for key, value in item.items():
                line.append(f"{key}: {value}")
            result.append(" | ".join(line))
        return "\n".join(result)
    
    @staticmethod
    def sort_documents(doc_list):
        """
        Sorts a list of documents by date.
    
        Parameters
        ----------
        doc_list : list
            A list of dictionaries representing documents.
    
        Returns
        -------
        list
            The list of documents sorted by date.
        """
        
        result = []
        for doc in doc_list:
            title = CaseScraper.remove_extra_whitespace(doc.find("div", class_="views-field-title").get_text(strip=True))
            link = doc.find("a", class_="pdf-link")["href"]
            date_obj = CaseScraper.get_document_date(doc)
            result.append({"docTitle": title, "docLink": link, "docDateObj": date_obj})
        return sorted(result, key=lambda k: k["docDateObj"])
