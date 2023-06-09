import datetime

import langchain.schema
import openai
import regex as re
import os
# from case_scraper.pdf_functions import needs_ocr, extract_pdf_content_ocr
from langchain.chains import ConversationalRetrievalChain
# from langchain.indexes import VectorstoreIndexCreator
# from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.callbacks import get_openai_callback
# import pinecone

# pinecone_API_KEY = "71443f75-d244-4466-b33e-ea17b36f6a94"
# pinecone.init(
#         api_key=pinecone_API_KEY,
#         environment="us-west4-gcp-free"
#         )
#
# index_name = "doj-docs"
#



os.environ["OPENAI_API_KEY"] = "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"

#TODO: create a function that will calculate the time from case_open_date to final_judgment.
## for final judgments, always check the dates of the final judgment document and take the later date for the timeline calculation.
#TODO: create a function that feeds the pdf text in chatgpt and extracts the relevant product definition, the geographic market, the names of the attorneys, and complete list of plaintiffs.

import pandas as pd
from typing import List, Dict
def unpack_column_dict(col: List[Dict]) -> str:
    """
    Unpack df column dictionary into a string.
    :param col: DataFrame column containing document dictionaries
    :return: string, concatenated document titles and dates
    """
    string = ""
    # Remove duplicate rows
    if pd.isna(col).all():
        return col
    for document_dict in col:
        if "docTitle" in document_dict and "docDateObj" in document_dict:
            document_dict["docTitle"] = document_dict["docTitle"].replace("\n", "")
            string += f"{document_dict['docTitle']} - {document_dict['docDateObj']}\n\n"
    return string
def unpack_key_docs(col: Dict[str, List[Dict]]) -> str:
    """
    Unpack df column dictionary into a string.
    :param col: DataFrame column dictionary containing document dictionaries
    :return: string, concatenated document titles and dates
    """
    complaints = col.get("complaint", [])
    jdmt = col.get("judgment", [])
    settle = col.get("settlements", [])
    dismiss = col.get('dismiss', [])
    documents = complaints + jdmt + settle + dismiss
    documents = [doc for doc in documents if "docTitle" in doc and "docDateObj" in doc]
    string = '\n'.join(["{0} - {1}".format(doc['docTitle'].replace('\n', ''),doc['docDateObj']) for doc in documents])
    return string

import re
from collections import OrderedDict
def dedup_string(string: str) -> str:
    """
    Remove duplicate words in a given string.
    :param string: input string
    :return: string, deduplicated string
    """
    # Remove punctuation and convert to lowercase
    string = re.sub(r'[^\w\s]', '', string.lower())
    input_words = string.split()
    unique_words = OrderedDict.fromkeys(input_words)
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

import requests
def is_pdf_link(url: str) -> bool:
    """
    Check if the given URL points to a PDF file.
    :param url: str, the URL to check
    :return: bool, True if the URL points to a PDF, False otherwise
    """
    try:
        # Send a HEAD request to get the response headers
        response = requests.head(url, allow_redirects=True)
        content_type = response.headers.get('Content-Type', '').lower()
        # Check if the Content-Type header indicates a PDF file
        return content_type == 'application/pdf'
    except requests.RequestException:
        # Return False if any errors occur while requesting the URL
        return False


openai.api_key =  "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"




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
from langchain.text_splitter import CharacterTextSplitter
def split_document_into_chunks(document: str or list) -> list:
    """
    Split the given document into chunks of a specified size.
    :param document: str or list, the document to be split
    :return: list, the chunks of the document
    """
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    if isinstance(document, str):
        chunks = text_splitter.split_text(document)
    else:
        chunks = text_splitter.split_documents(document)
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


def fine_tune_embeddings(embeddings, documents, text_processor, epochs=10):
    # Tokenize and preprocess the documents
    processed_docs = [text_processor.process(doc) for doc in documents]
    # Fine-tune the embeddings using the processed documents
    embeddings.finetune(processed_docs, epochs=epochs)

# Create embeddings using the OpenAI API
def create_embeddings_from_text_chunks(text_chunks):
    
    embeddings = OpenAIEmbeddings()
    # knowledge_base = Pinecone.from_documents(text_chunks, embeddings, index_name=index_name)
    if isinstance(text_chunks[0], langchain.schema.Document):
        knowledge_base = Chroma.from_documents(text_chunks,
                                               embeddings)  # if using chroma, make sure to modify the search type to mmr in the query_text function.
    else:
        knowledge_base = Chroma.from_texts(text_chunks, embeddings)



    return knowledge_base

def query_text(query, knowledge_base, chat_history=None):
    # if vector_db_type:
    #     if vector_db_type.lower() == "chroma":
    retriever = knowledge_base.as_retriever(search_type="mmr", search_kwargs={"k":5})

    # else:
    #     retriever = knowledge_base.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    llm = ChatOpenAI(model_name="gpt-4")

    qa = ConversationalRetrievalChain.from_llm(llm, retriever)
 
    if isinstance(query, list):

        chat_history = []
        answers = []
        for question in query:
            with get_openai_callback() as cb:
                result = qa({"question":question + " If you do not know the answer, state N/A", "chat_history":chat_history})
                chat_history += result["chat_history"]
                answers.append((question, result["answer"], cb))
        return answers, result["chat_history"]
    else:
        with get_openai_callback() as cb:
            result = qa({"question":query + " If you do not know the answer, state N/A", "chat_history":chat_history})
        return (query, result["answer"], cb), result["chat_history"]

def openaipricing(nb_tokens_used: int, model_name: str = None, embeddings=False, chatgpt=False) -> float:
    """
    Return cost per token in dollars for either GPT models or embeddings
    Args:
        nb_tokens_used: total token used by model
        model_name: llm model
        chatgpt: toggle gpt model compute cost
        embeddings: toggle embedding to compute tokens used cost

    Returns: cost
    """
    if not isinstance(nb_tokens_used, int):
        raise TypeError(
            f"nb_tokens_used Expected object of type int, got: {type(model_name)}"
        )
    if model_name and not isinstance(model_name, str):
        raise TypeError(
            f"model_name Expected object of type str, got: {type(model_name)}"
        )
    if chatgpt:
        #  GPT 4 has 2 prices
        #  [REQUEST] Prompt tokens: 0.03 USD per 1000 tokens are the parts of words fed into GPT-4
        #  [RESPONSE] while completion tokens are the content generated by GPT-4 at 0.06 USD per 1000 tokens
        model_costs = {
            'gpt-4': 0.03,
            'gpt-3.5-turbo': 0.002,
            'davinci': 0.02,
            'babbage': 0.0005,
            'curie': 0.002,
            'ada': 0.0004,
            'turbo': 0.002
        }
        cost = model_costs.get(model_name, 1)
        return (cost / 1000.) * nb_tokens_used
    elif embeddings:
        # text-embedding-ada-002
        return (0.0004 / 1000.) * nb_tokens_used
    # elif (chatgpt and embeddings):
    #     model_costs = {
    #         'gpt-4': 0.03,
    #         'gpt-3.5-turbo': 0.002,
    #         'davinci': 0.02,
    #         'babbage': 0.0005,
    #         'curie': 0.002,
    #         'ada': 0.0004,
    #         'turbo': 0.002
    #     }
    #     cost = model_costs.get(model_name, 1)
    #     chatgpt_cost =  (cost / 1000.) * nb_tokens_used
    #     embeddings_cost = (0.0004 / 1000.) * nb_tokens_used
    #     return chatgpt_cost + embeddings_cost

    else:
        raise ValueError("Invalid option")
# def load_pdf_temporarily(url):
#     from langchain.document_loaders import PyPDFLoader
#     # Download the PDF file
#
#     response = requests.get(url)
#
#     file_path = "temp.pdf"
#
#     with open(file_path, 'wb') as f:
#         f.write(response.content)
#
#     # no need to open the file for needs_ocr, it can handle a file path directly
#     if needs_ocr(file_path):
#         with open(file_path, 'rb') as f_ocr:
#             text = extract_pdf_content_ocr(f_ocr)
#             text = text.encode()
#         # Overwrite the file with OCR extracted content
#         with open(file_path, 'wb') as f_write:
#             f_write.write(text)
#
#     # Process the PDF
#     try:
#         document = PyPDFLoader(file_path).load()
#         return document
#     except:
#         import fitz
#         doc = fitz.open(stream=open(file_path, "rb").read(), filetype="pdf")
#         text = ""
#         for page_num in range(len(doc)):
#             page = doc.load_page(page_num)
#             text += page.get_text()
#         return text
#     finally:
#         # Delete the file
#         if os.path.exists(file_path):
#             os.remove(file_path)
#         else:
#             print("The file does not exist")

def find_complaint(dictionary_list):
    for dictionary in dictionary_list:
        if dictionary.get('title') == 'complaint':
            return dictionary
    return None
import pickle

def load_pickle_data(filepath):
    """
    This function loads data from a pickle file.

    Parameters:
    filepath (str): The path of the pickle file.

    Returns:
    data: The data loaded from the pickle file.

    Business Logic:
    This function uses Python's built-in 'pickle' module to deserialize
    data from the pickle file. This can be useful when you have preprocessed
    or transformed data that you want to reuse across different scripts or
    sessions. By loading this data from a pickle file, we can avoid
    having to redo potentially expensive computations or fetch data
    from a remote source, which can make our program more efficient and
    faster to develop.
    """
    
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    
    return data

# Example usage:



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
