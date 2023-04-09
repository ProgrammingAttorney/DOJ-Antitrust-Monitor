import datetime
import pandas as pd
from collections import Counter

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
