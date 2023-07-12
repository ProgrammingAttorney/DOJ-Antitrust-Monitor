#Key sec_MDOhZ8qaY3UOhDhVQgAenKDUVrIDsSZAimport requests

import requests

class ChatPDF:
	def __init__(self, api_key):
		self.api_key = api_key
		self.headers = {'x-api-key': self.api_key, "Content-Type": "application/json"}
	
	def add_pdf_via_url(self, url):
		"""
		Add a PDF to ChatPDF via a publicly accessible URL.

		Parameters:
		url (str): The URL where the PDF is located.

		Returns:
		dict: The response from the API, which includes the source ID of the added PDF.
		"""
		data = {'url': url}
		response = requests.post('https://api.chatpdf.com/v1/sources/add-url', headers=self.headers, json=data)
		return response.json()
	
	def add_pdf_via_file_upload(self, file_path):
		"""
		Add a PDF to ChatPDF by uploading a file.

		Parameters:
		file_path (str): The path to the PDF file on the local machine.

		Returns:
		dict: The response from the API, which includes the source ID of the added PDF.
		"""
		with open(file_path, 'rb') as f:
			files = {'file': f}
			response = requests.post('https://api.chatpdf.com/v1/sources/add-file', headers=self.headers, files=files)
		return response.json()
	
	def chat_with_pdf(self, source_id, messages):
		"""
		Send a chat message to a PDF file using its source ID.

		Parameters:
		source_id (str): The source ID of the PDF.
		messages (list): A list of dictionaries, each containing a 'role' (either 'user' or 'assistant') and 'content' (the message content).

		Returns:
		dict: The response from the API, which includes the chat message response.
		"""
		data = {'sourceId': source_id, 'messages': messages}
		response = requests.post('https://api.chatpdf.com/v1/chats/message', headers=self.headers, json=data)
		return response.json()
	
	def delete_pdf(self, source_ids):
		"""
		Delete one or multiple PDF files from ChatPDF using their source IDs.

		Parameters:
		source_ids (list): A list of source IDs that you want to delete.

		Returns:
		int: The status code from the API. If successful, it should return 200.
		"""
		data = {'sources': source_ids}
		response = requests.post('https://api.chatpdf.com/v1/sources/delete', headers=self.headers, json=data)
		return response.status_code
