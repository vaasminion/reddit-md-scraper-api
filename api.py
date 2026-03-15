import os

from flask import Flask
from flask_restful import Api

from config import MD_FILES
from resources import RedditScraper

app = Flask(__name__)
api = Api(app)
api.add_resource(RedditScraper, '/scrape')

if __name__ == '__main__':
    os.makedirs(MD_FILES, exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=False)
