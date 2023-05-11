from flask import Flask, render_template, jsonify, abort
from .views import *
from elasticsearch import Elasticsearch, exceptions as es_exceptions
es = Elasticsearch()
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')



app = Flask(__name__)

@app.route('/get_data')
def get_data():
    try:
        data = some_data_source.get_data()  # replace with your actual data source
        return jsonify(data)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        abort(500)  # return an internal server error



es = Elasticsearch()

try:
    es.index(index='my-index', id=1, body={'text': 'the text of your pdf'})
    es.search(index="my-index", body={"query": {"match": {'text':'keyword'}}})
except es_exceptions.ConnectionError as e:
    print(f"A connection error occurred: {str(e)}")
except es_exceptions.NotFoundError:
    print("The specified index does not exist")
except Exception as e:
    print(f"An error occurred: {str(e)}")


if __name__ == '__main__':
    app.run(debug=True)