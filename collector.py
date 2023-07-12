import jsonpickle

from case_scraper.scraper import CaseScraper
from case_scraper.chatpdf import *

def main():
	
	# Instantiate the CaseScraper class
	scraper = CaseScraper()
	
	# Step 1: Collect all HTML tables from DOJ's website
	case_rows = scraper.collect_HTML_tables()
	
	# Step 2: Iterate through the case rows
	case_data_list = []
	for case_row in case_rows:
		# Step 3: Extract case data from each row and store it as a dictionary
		case_data = scraper.extract_case_data_from_row(case_row)
		
		# Step 4: Store the case data into a list
		case_data_list.append(case_data)
	json_data = jsonpickle.encode(case_data_list)
	# Write the JSON string to a file
	with open('DOJ_case_data.json', 'w') as f:
		f.write(json_data)

if __name__ == "__main__":
	main()
