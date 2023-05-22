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
import pickle
with open(f"doj-data-{datetime.date.today().strftime('%m.%d.%Y')}", "wb") as f:
    pickle.dump(case_data_list, f)

for case_data in tqdm(case_data_list, desc="Answering Questions", ascii=False, ncols=75, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"):
    complaint = find_complaint(case_data["documents"])
    merger_type = "NA"
    consumation = "NA"
    industry = "NA"
    geographic_markets = "NA"
    product_markets = "NA"
    signing_date = "NA"
    if complaint:
        complaint_link = complaint["attachments"][0]["url"]


        documents = load_pdf_temporarily(complaint_link)


        texts = split_document_into_chunks(documents)
        knowledge_base = create_embeddings_from_text_chunks(texts)
        # merger type
        chat_history = []


        merger_type_query = query_text("What type of merger does the complaint challenge (Horizontal or Vertical)? Give a one word answer.", knowledge_base, chat_history)
        merger_type = merger_type_query[0][1]
        tokens_used += merger_type_query[0][-1].total_tokens
        chat_history += merger_type_query[-1]
        # consumated / unconsumated
        consumation_query = query_text("Is the complaint challenging a consummated or unconsummated merger? Give a one word answer.", knowledge_base, chat_history)
        consumation  = consumation_query[0][1]
        tokens_used += consumation_query[0][-1].total_tokens
        chat_history += consumation_query[-1]
        # industry
        industry_query = query_text("In what industry do the merging parties operate? Only provide the industry name.", knowledge_base,
                                       chat_history)
        industry  = industry_query[0][1]
        tokens_used += industry_query[0][-1].total_tokens
        chat_history += industry_query[-1]
        # relevant geographic markets
        geographic_markets_query = query_text("What are the relevant geographic markets alleged in the complaint? Only provide the relevant geographic markets.", knowledge_base,
                                              chat_history)
        geographic_markets  = geographic_markets_query[0][1]
        tokens_used += geographic_markets_query[0][-1].total_tokens
        chat_history += geographic_markets_query[-1]
        # relevant product markets
        product_markets_query = query_text("What are the relevant product markets alleged in the complaint? Only provide the relevant product markets.", knowledge_base,
                                           chat_history)
        product_markets = product_markets_query[0][1]
        tokens_used += product_markets_query[0][-1].total_tokens
        chat_history += product_markets_query[-1]
        # merger signing date
        signing_date_query = query_text("When did the defendants sign their agreement? Give only the date of signing", knowledge_base,
                                           chat_history)
        signing_date = signing_date_query[0][1]
        tokens_used += signing_date_query[0][-1].total_tokens
        chat_history += signing_date_query[-1]

    case_data.update({
        "Merger Type": merger_type,
        "Consummation Status": consumation,
        "Industry": industry,
        "Relevant Geographic Markets": geographic_markets,
        "Relevant Product Markets": product_markets,
        "Signing Date": signing_date

    })

with open('DOJdata.json', 'w') as f:
    json.dump(case_data_list, f)

print("Total Cost for 100 cases:", openaipricing(tokens_used, "gpt-4", embeddings=True, chatgpt=True))
# synopsis
    # synopsis_query =
    # if you use a list of questions, the return is going to be a tuple containing a list of Q&A tuples as well as the chat_history --- (answers, result["chat_history"])
    # if you ask a single question, the return is going to be a tuple containing a Q&A tuple and the chat history )(query, result["answer"]), result["chat_history"])
    # if you ask a single question, make sure to upload the chat history
    # results = query_text(query, knowledge_base, [])

# questions_list = ["Will the merger harm consumers? If so how? Provide a comprehensive answer"
# "Will the merger reduce innovation? If so how? Provide a comprehensive answer",
# "Will the merger reduce head-to-head competition? If so how? Provide a comprehensive answer",
# "Will the merger eliminate potential competition? If so how? Provide a comprehensive answer",
# "Will the merger harm competitors? If so how? Provide a comprehensive answer",
# "Will the merger facilitate coordination among competitors? If so how? Provide a comprehensive answer",
#                   "what are the relevant product markets alleged in the complaint? Provide a comprehensive answer.",
#                   "what are the relevant geographic markets alleged in the complaint? Provide a comprehensive answer.",
#                   "what remedies did the merging parties propose? Provide a comprehensive answer."]