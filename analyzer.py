import jsonpickle
from case_scraper.scraper import CaseScraper
from case_scraper.chatpdf import *

# Step 5: Iterate through the list of case data and access the case_link attribute
with open('DOJ_case_data.json', 'r') as f:
    json_data = f.read()

case_data_list = jsonpickle.decode(json_data)
for case_data in case_data_list:
    # case_link = case_data.get("case_link")
    #
    # # Step 6: Extract case details from the case page
    # case_details = scraper.extract_case_details_from_casepage(case_link)

    # documents = case_details.get("documents")
    documents = case_data.get("documents")

    # Step 8: Iterate through the list of tuples and get the link to each case document page
    for document in documents:
        if "complaint" in document.get("doc_name").lower():
            complaint_link = document.get("links")[0]
            chatpdf = ChatPDF("APIKEY")

            # Add a PDF via URL
            response = chatpdf.add_pdf_via_url(complaint_link)


            # Chat with a PDF
            source_id = response["sourceId"]
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
