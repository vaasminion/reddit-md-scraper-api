import os

from flask import Flask
from flask_restful import Api
from flasgger import Swagger

from config import MD_FILES
from resources import RedditScraper, RedditScraperV2

app = Flask(__name__)
api = Api(app)
api.add_resource(RedditScraper, '/scrape')
api.add_resource(RedditScraperV2, '/v2/scrape')

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/",
    "swagger_ui_config": {
        "persistAuthorization": True,
    },
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Reddit Scraper API",
        "description": (
            "API for scraping Reddit subreddits and returning markdown files.\n\n"
            "Use the **Authorize** button to set your `X-API-Key`. "
            "Leave blank if the server is running without authentication."
        ),
        "version": "1.0.0",
    },
    "securityDefinitions": {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key passed via the X-API-Key header. Leave blank if auth is disabled.",
        }
    },
    "security": [{"ApiKeyAuth": []}],
}

Swagger(app, config=swagger_config, template=swagger_template)

if __name__ == '__main__':
    os.makedirs(MD_FILES, exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=False)
