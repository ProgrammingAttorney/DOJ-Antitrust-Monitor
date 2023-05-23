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

case_data_list = load_pickle_data("doj-data-5.18.pkl")
tokens_used = 0
for case_data in tqdm(case_data_list, desc="Answering Questions", ascii=False, ncols=75, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"):
    complaint = find_complaint(case_data["documents"])
    merger_type = "NA"
    consumation = "NA"
    industry = "NA"
    geographic_markets = "NA"
    product_markets = "NA"
    signing_date = "NA"
    chat_history = []
    if complaint:
        complaint_link = complaint["attachments"][0]["url"]


        documents = load_pdf_temporarily(complaint_link)


        texts = split_document_into_chunks(documents)
        knowledge_base = create_embeddings_from_text_chunks(texts)
        # merger type



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

with open(f"doj-data-{datetime.date.today().strftime('%m.%d.%Y')}", "wb") as f:
    pickle.dump(case_data_list, f)

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