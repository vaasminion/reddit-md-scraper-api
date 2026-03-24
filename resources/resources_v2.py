import os
from datetime import datetime, timezone

from flask import send_file
from flask_restful import Resource, reqparse

from auth import require_api_key
from logger import logger
from scraper.scraper_v2 import scrape_reddit_sub_v2
from utils import generate_id_random


class RedditScraperV2(Resource):
    _args = reqparse.RequestParser()
    _args.add_argument("subreddit", type=str, required=True)
    _args.add_argument("category", type=str)
    _args.add_argument("traceid", type=str)

    @require_api_key
    def post(self):
        """Scrape a Reddit subreddit using Scrapling and return a markdown file.
        ---
        tags:
          - Scraper
        security:
          - ApiKeyAuth: []
        parameters:
          - name: subreddit
            in: formData
            type: string
            required: true
            description: Name of the subreddit to scrape (e.g. "python")
          - name: category
            in: formData
            type: string
            required: false
            description: Post category to fetch (hot | new | top | best). Defaults to "best".
            enum: [hot, new, top, best]
          - name: traceid
            in: formData
            type: string
            required: false
            description: Optional trace ID for request tracking.
        responses:
          200:
            description: Markdown file containing the scraped subreddit posts.
            content:
              text/markdown:
                schema:
                  type: string
                  format: binary
          401:
            description: Missing API key.
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: Missing API key
          403:
            description: Invalid API key.
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: Invalid API key
          500:
            description: Internal server error.
            schema:
              type: object
              properties:
                error:
                  type: string
        """
        traceid = None
        try:
            request_data = self._args.parse_args()
            subreddit = request_data.get('subreddit', None)
            category = request_data.get('category') or 'best'
            traceid = request_data.get('traceid') or generate_id_random(5)
            utc_now = datetime.now(timezone.utc)

            logger.info(f"[{traceid}] POST /v2/scrape — subreddit: {subreddit} | category: {category}")

            if not subreddit:
                raise Exception('Empty Subreddit Name')

            mdfile = scrape_reddit_sub_v2(
                reddit_page=subreddit,
                category=category,
                traceid=traceid,
                utc_now=utc_now,
            )

            logger.info(f"[{traceid}] Sending file to client: {os.path.basename(mdfile)}")
            return send_file(
                mdfile,
                mimetype='text/markdown',
                as_attachment=True,
                download_name=os.path.basename(mdfile),
            )
        except Exception as e:
            logger.exception(f"Request failed [traceid={traceid}]: {e}")
            return {"error": str(e)}, 500
