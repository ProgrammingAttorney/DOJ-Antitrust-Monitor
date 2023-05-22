import os
import json
import time
from langchain.embeddings.openai import OpenAIEmbeddings

from case_scraper.utilities import *
from tqdm import tqdm
from case_scraper.pdf_functions import *
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import ElasticVectorSearch, Pinecone, Weaviate, FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
import openai

from case_scraper.scraper import *
from pprint import pprint

import pickle
# Step 1: Collect all HTML tables from DOJ's website

# os.environ["OPENAI_API_KEY"] = "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"

rows = collect_HTML_tables()

# Step 2: Iterate through the case rows
case_data_list = []
for row in rows:
	# Step 3: Extract case data from each row and store it as a dictionary
	case_data = extract_case_data_from_row(row)
	# Step 4: Store the case data into a list
	case_data_list.append(case_data)

# Step 5: Iterate through the list of case data and access the case_link attribute
tokens_used = 0
for case_data in tqdm(case_data_list, desc="Collecting Data", ascii=False, ncols=75,  bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"):
	case_link = case_data['case_link']
	# Step 6: Extract case details from the case page
	case_details = extract_case_details_from_casepage(case_link)
	# Step 7: Access the "documents" key which will have a list of tuples
	documents = case_details['documents']
	# Step 8: Iterate through the list of tuples and get the link to each case document page
	for idx, document in enumerate(documents.copy()):
		document_link = document[1]
		# Step 9: Get document details from each document page
		document_details = get_document_details_from_document_page(document_link)
		# Step 10: Do something with the document details
		documents[idx] = document_details
		# process_document_details(document_details)
	case_data.update(case_details)

with open(f"doj-data-{datetime.date.today().strftime('%m.%d.%Y')}", "wb") as f:
	pickle.dump(case_data_list, f)