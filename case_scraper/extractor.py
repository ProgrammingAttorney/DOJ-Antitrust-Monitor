import re
from datetime import datetime
from typing import List, Optional, Dict, Union

# Maintain a list of presidents and their terms sorted by start date
PRESIDENTS = [
    {"name": "Joe Biden", "start": datetime(2021, 1, 20), "end": None},
    # Add more presidents and their terms as needed
]

def find_president(date: datetime) -> str:
    """
    Find the sitting US President on a given date.

    :param date: A datetime object representing the date.
    :return: A string containing the name of the sitting US President.
    """
    for president in PRESIDENTS:
        if president["end"] is None or date <= president["end"]:
            if date >= president["start"]:
                return president["name"]

    return "Unknown"

def get_document_date(text: str) -> Optional[datetime]:
    """
    Extract the document date from a given text.

    :param text: A string containing the text to search for a date.
    :return: A datetime object representing the extracted date, or None if no date is found.
    """
    date_formats = [
        "%B %d, %Y",
        "%m/%d/%Y",
        "%Y-%m-%d",
    ]

    date_pattern = r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b|\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{4})\b"
    date_match = re.search(date_pattern, text)

    if date_match:
        date_str = date_match.group(0)
        for date_format in date_formats:
            try:
                return datetime.strptime(date_str, date_format)
            except ValueError:
                continue

    return None

def unpackColumnDict(column_data: List[Dict[str, Union[str, datetime]]]) -> str:
    """
    Unpack the data in a dictionary column into a single string.

    :param column_data: A list of dictionaries containing the column data.
    :return: A string containing the unpacked column data.
    """
    if not column_data:
        return ""

    return "\n".join([f'{d["docTitle"]} ({d["docDate"]}): {d["docLink"]}' for d in column_data])
