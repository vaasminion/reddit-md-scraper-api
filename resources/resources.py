import os
from datetime import datetime, timezone

from flask import send_file
from flask_restful import Resource, reqparse

from auth import require_api_key
from logger import logger
from scraper import scrape_RedditSub
from utils import generate_id_random


class RedditScraper(Resource):
    request_deploy_arg = reqparse.RequestParser()
    request_deploy_arg.add_argument("subreddit", type=str, required=True)
    request_deploy_arg.add_argument("category", type=str)
    request_deploy_arg.add_argument("traceid", type=str)

    @require_api_key
    def post(self):
        traceid = None
        try:
            requestdata = self.request_deploy_arg.parse_args()
            subreddit = requestdata.get('subreddit', None)
            category = requestdata.get('category') or 'best'  # hot | new | top | best
            traceid = requestdata.get('traceid') or generate_id_random(5)
            utc_now = datetime.now(timezone.utc)

            logger.info(f"[{traceid}] POST /scrape — subreddit: {subreddit} | category: {category}")

            if subreddit is None or subreddit == '':
                raise Exception('Empty Subreddit Name')

            mdfile = scrape_RedditSub(reddit_page=subreddit, category=category, traceid=traceid, utc_now=utc_now)

            logger.info(f"[{traceid}] Sending file to client: {os.path.basename(mdfile)}")
            return send_file(
                mdfile,
                mimetype='text/markdown',
                as_attachment=True,
                download_name=os.path.basename(mdfile)
            )
        except Exception as e:
            logger.exception(f"Request failed [traceid={traceid}]: {e}")
            return {"error": str(e)}, 500
