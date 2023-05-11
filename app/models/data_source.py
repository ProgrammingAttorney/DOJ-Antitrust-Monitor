import json

def get_data():
    try:
        with open('path_to_your_file.json', 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print("The specified JSON file does not exist")
        return None
    except json.JSONDecodeError:
        print("An error occurred while decoding the JSON file")
        return None
