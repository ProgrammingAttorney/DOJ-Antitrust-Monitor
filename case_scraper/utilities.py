import datetime
import pandas as pd
import requests
import openai
from collections import Counter
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback
import os

os.environ["OPENAI_API_KEY"] = "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"
#TODO: create a function that will calculate the time from case_open_date to final_judgment.
## for final judgments, always check the dates of the final judgment document and take the later date for the timeline calculation.
#TODO: create a function that feeds the pdf text in chatgpt and extracts the relevant product definition, the geographic market, the names of the attorneys, and complete list of plaintiffs.

def unpackColumnDict(col):
    """
    Unpack df column dictionary into a string.
    :param col: DataFrame column containing document dictionaries
    :return: string, concatenated document titles and dates
    """
    # Place the code for unpackColumnDict function here
    string = ""
    # Remove duplicate rows
    if pd.isna(col).all():
        return col
    for document_dict in col:
        document_dict["docTitle"] = document_dict["docTitle"].replace("\n", "")
        string += f"{document_dict['docTitle']} - {document_dict['docDateObj']}\n\n"
    return string

def unpackKeyDocsDicts(col):
    """
    Unpack df column dictionary into a string.
    :param col: DataFrame column containing document dictionaries
    :return: string, concatenated document titles and dates
    """
    # Place the code for unpackKeyDocsDicts function here
    string = ""
    complaints = col["complaint"]
    jdmt = col["judgment"]
    settle = col["settlements"]
    dismiss = col['dismiss']

    for doc_dict in complaints + jdmt + settle + dismiss:
        doc_dict["docTitle"] = doc_dict["docTitle"].replace("\n", "")
        string += f"{doc_dict['docTitle']} - {doc_dict['docDateObj']}\n"

    return string
def deDupString(string):
    """
    Remove duplicate words in a given string.
    :param string: input string
    :return: string, deduplicated string
    """
    # Place the code for deDupString function here
    input_words = string.split(" ")
    unique_words = Counter(input_words)
    deduplicated_string = " ".join(unique_words.keys())
    return deduplicated_string

def find_president(date: datetime.datetime):
    """
    Find the president of the United States at the given date.
    :param date: datetime.datetime object, date for which the president is to be determined
    :return: string, name of the president at the given date
    """
    # Place the code for find_president function here
    presidents =   {
            "George W. Bush": {"start": datetime.datetime(2001, 1, 20), "end": datetime.datetime(2009, 1, 19)},
            "Barack Obama": {"start": datetime.datetime(2009, 1, 20), "end": datetime.datetime(2017, 1, 20)},
            "Donald Trump": {"start": datetime.datetime(2017, 1, 20), "end": datetime.datetime(2021, 1, 20)},
            "Joe Biden": {"start": datetime.datetime(2021, 1, 20), "end": datetime.datetime.now()},
        }
        # Loop through the dictionary and find the president
    for president, dates in presidents.items():
        if dates["start"] <= date <= dates["end"]:
            return president
    return None

# Other utility functions should be placed here

def is_pdf_link(url):
    try:
        response = requests.head(url, allow_redirects=True)
        content_type = response.headers.get('Content-Type', '').lower()
        return content_type == 'application/pdf'
    except requests.RequestException:
        return False


openai.api_key =  "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"

import openai
import regex as re
import faiss
import numpy as np
# model = SentenceTransformer('sentence-transformers/distilbert-base-nli-mean-tokens')


def preprocess_text(text):
    # Remove special characters and multiple spaces
    text = re.sub(r'\s+', ' ', text)

    # Split the text into paragraphs using a digit followed by a period as a delimiter
    paragraphs = re.split(r'(?<=\d)\.\s+', text)

    # Strip leading and trailing spaces from paragraphs
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    return paragraphs
#
# Split the document into paragraphs
def split_document_into_chunks(document):

    from langchain.text_splitter import CharacterTextSplitter
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=2000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(document)
    return chunks
questions_list = ["Will the merger harm consumers? If so how? Provide a comprehensive answer"
"Will the merger reduce innovation? If so how? Provide a comprehensive answer",
"Will the merger reduce head-to-head competition? If so how? Provide a comprehensive answer",
"Will the merger eliminate potential competition? If so how? Provide a comprehensive answer",
"Will the merger harm competitors? If so how? Provide a comprehensive answer",
"Will the merger facilitate coordination among competitors? If so how? Provide a comprehensive answer",
                  "what are the relevant product markets alleged in the complaint? Provide a comprehensive answer.",
                  "what are the relevant geographic markets alleged in the complaint? Provide a comprehensive answer.",
                  "what remedies did the merging parties propose? Provide a comprehensive answer."]
# Create embeddings using the OpenAI API
def create_embeddings_from_text_chunks(text_chunks):
    embeddings = OpenAIEmbeddings()
    knowledge_base = FAISS.from_texts(text_chunks, embeddings)
    return knowledge_base

def query_text(query, knowledge_base):
    docs = knowledge_base.similarity_search(query)
    llm = OpenAI()
    chain = load_qa_chain(llm, chain_type="stuff")
    with get_openai_callback() as cb:
        response = chain.run(input_documents=docs, question = query)
        print(response)
        print(cb)

#
#
# def create_embeddings(model, paragraphs):
#     embeddings = model.encode(paragraphs)
#     return np.array(embeddings)
#
# # Build a semantic index using FAISS
# def build_semantic_index(embeddings):
#     index = faiss.IndexFlatL2(embeddings.shape[1])
#     index.add(embeddings)
#     return index


# Create an embedding for the question
def create_question_embedding(model, question):
    return model.encode([question])

# Search for the top-k most similar paragraphs
def search_similar_paragraphs(index, question_embedding, k=15):
    distances, indices = index.search(question_embedding, k)
    return indices[0]

# Answer the question using the retrieved paragraphs
# def answer_question(api_key, model_name, question, context):
#     openai.api_key = api_key
#
#     full_context = "\n".join(context)
#     prompt = f"""You are a helpful assistant that answers questions only using information provided to you in the prompt. If you ask me a question for which the answer is present in the prompt, I will give you the answer. If you ask me a question that I cannot answer based on the prompt, I will respond with 'No idea.\n\n<<Prompt>> {full_context}\n\n<<Questions>>\nQ1: {question}""",
#
#     response = openai.Completion.create(
#         model="text-davinci-003",
#         prompt = prompt,
#         temperature = 0,
#         top_p=.5,
#         max_tokens = 100,
#         frequency_penalty = 0.0,
#         presence_penalty=0.0,
#         stop=["\n."]
#     )
#     return response["choices"][0]["text"]
# if __name__ == '__main__':
#
#
# from case_scraper.utilities import *
#
# api_key = "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"
#
# document = ""
# model_name = "gpt-3.5-turbo"
# from sentence_transformers import SentenceTransformer
#
#
# model = SentenceTransformer('sentence-transformers/distilbert-base-nli-mean-tokens')
# # Step 1: Split the document into paragraphs
# paragraphs = split_document_into_chunks(document)
#
# # Step 2: Create embeddings for each paragraph
# embeddings = create_embeddings(model, paragraphs)
#
# # Step 3: Store the embeddings in a FAISS index
# index = build_semantic_index(embeddings)
#
# question = "When was the proposed merger that is the subject of this litigation announced?"
#
# # Step 1: Create an embedding for the question
# question_embedding = create_question_embedding(model, question)
#
# # Step 2: Perform a similarity search to find the top-k most similar paragraphs
# top_k_indices = search_similar_paragraphs(index, question_embedding, k=15)
#
# # Step 3: Answer the question based on the retrieved paragraphs
# top_k_paragraphs = [paragraphs[i] for i in top_k_indices]
# answer = answer_question(api_key, model_name, top_k_paragraphs, question)
# print(answer)
