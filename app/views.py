from flask import render_template, jsonify, abort
from .models.data_source import get_data
from elasticsearch import Elasticsearch, exceptions as es_exceptions
from app import app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_data')
def get_data_route():
    try:
        data = get_data()
        if data is None:
            abort(500)  # return an internal server error
        else:
            return jsonify(data)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        abort(500)  # return an internal server error


# You can place your Elasticsearch code here as well
# depending on your specific requirements and project structure
