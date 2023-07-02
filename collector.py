from case_scraper.scraper import CaseScraper
from case_scraper.chatpdf import *

def main():
	
	# Instantiate the CaseScraper class
	scraper = CaseScraper()
	
	# Step 1: Collect all HTML tables from DOJ's website
	case_rows = scraper.collect_HTML_tables()
	
	# Step 2: Iterate through the case rows
	case_data_list = []
	for case_row in case_rows:
		# Step 3: Extract case data from each row and store it as a dictionary
		case_data = scraper.extract_case_data_from_row(case_row)
		
		# Step 4: Store the case data into a list
		case_data_list.append(case_data)
	
	# Step 5: Iterate through the list of case data and access the case_link attribute
	for case_data in case_data_list:
		case_link = case_data.get("case_link")
		
		# Step 6: Extract case details from the case page
		case_details = scraper.extract_case_details_from_casepage(case_link)
		
		# Step 7: Access the "documents" key from each case
		documents = case_details.get("documents")
		
		# Step 8: Iterate through the list of tuples and get the link to each case document page
		for document in documents:
			doc_page_link = document.get("doc_link")
			
			# Step 9: Get document details from each document page
			doc_details = scraper.get_document_details_from_document_page(doc_page_link)
			
			# Step 10: Get the link to the document with the title complaint
			if doc_details.get("title").lower() == "complaint":
				complaint_link = doc_details.get("url")
				chatpdf = ChatPDF(CP_API_KEY)
				
				# Add a PDF via URL
				response = chatpdf.add_pdf_via_url(complaint_link)
				print(response)
				
				# Chat with a PDF
				source_id = 'source_id_of_the_pdf'
				messages = [{'role': 'user', 'content': 'What is the title of the document?'}]
				response = chatpdf.chat_with_pdf(source_id, messages)
				print(response)
				
				# Delete a PDF
				source_ids = ['source_id_of_the_pdf']
				status_code = chatpdf.delete_pdf(source_ids)
				print(status_code)

# Step 11: Do something with the document
				# For example, print the link to the complaint document
				print(f"Link to the complaint document: {complaint_link}")

if __name__ == "__main__":
	main()
