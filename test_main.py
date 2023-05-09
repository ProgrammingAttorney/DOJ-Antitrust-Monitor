import os

from langchain.embeddings.openai import OpenAIEmbeddings
from case_scraper.utilities import *
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
for case_data in case_data_list[0:10]:
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
    pass
pprint(case_data_list)

# We need to split the text that we read into smaller chunks so that during information retreival we don't hit the token size limits.
# complaint = find_complaint(case_data["documents"])
# complaint_link = complaint["attachments"][0]["url"]
# documents = load_pdf_temporarily(complaint_link)
#texts = text_splitter.split_documents(documents)
#query_text
# chunks = split_document_into_chunks(text)
# knowledge_base = create_embeddings_from_text_chunks(texts)
# if you use a list of questions, the return is going to be a tuple containing a list of Q&A tuples as well as the chat_history --- (answers, result["chat_history"])
# if you ask a single question, the return is going to be a tuple containing a Q&A tuple and the chat history )(query, result["answer"]), result["chat_history"])
# if you ask a single question, make sure to upload the chat history




# text_splitter = CharacterTextSplitter(
#     separator = "\n",
#     chunk_size = 1000,
#     chunk_overlap  = 200,
#     length_function = len,
# )
# texts = text_splitter.split_text(text)
#
# # Download embeddings from OpenAI
# embeddings = OpenAIEmbeddings()
# docsearch = FAISS.from_texts(texts, embeddings)
# chain = load_qa_chain(OpenAI("gpt-4"), chain_type="stuff")
# query = "who are the authors of the article?"
# docs = docsearch.similarity_search(query)
# chain.run(input_documents=docs, question=query)