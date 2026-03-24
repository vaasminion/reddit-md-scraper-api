import os
import time

from scrapling import Fetcher

from config import MD_FILES
from logger import logger
from scraper.scraper import get_comments, get_sub_url


_fetcher = Fetcher()


def _fetch_json(url, traceid, retries=3):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    for attempt in range(1, retries + 1):
        try:
            response = _fetcher.get(url, headers=headers, timeout=15)
            if response.status == 429:
                logger.warning(f"[{traceid}] Rate limited (429) on attempt {attempt}/{retries}: {url}")
                if attempt < retries:
                    time.sleep(3 * attempt)
                    continue
                raise Exception(f"Rate limited after {retries} attempts: {url}")
            return response.json()
        except Exception as e:
            logger.error(f"[{traceid}] Error fetching {url} (attempt {attempt}/{retries}): {e}")
            if attempt < retries:
                time.sleep(3)
                continue
            raise


def scrape_reddit_post_v2(url, traceid):
    logger.debug(f"[{traceid}] Fetching post (v2): {url}")
    comment_data = _fetch_json(url, traceid)

    result = ''
    for userpost in comment_data[0]['data']['children']:
        author_name = userpost['data']['author']
        post_content = userpost['data']['selftext']
        title = userpost['data']['title']

        logger.debug(f"[{traceid}] Post scraped — title: '{title}' | author: {author_name}")

        result += f'[TITLE] :: {title} \n'
        result += f'[AUTHOR_NAME] :: {author_name} \n'
        result += f'[URL] :: {url}\n'
        result += f'[BODY] :: {post_content} \n'

    comment_list = comment_data[1]['data']['children']
    logger.debug(f"[{traceid}] Parsing {len(comment_list)} top-level comments for: {url}")
    comments = ''
    try:
        comments = get_comments(comment_list)
    except Exception as e:
        logger.error(f"[{traceid}] Error parsing comments for {url}: {e}")
    if comments:
        result += f'[COMMENTS] :: {comments} \n'
    return result


def scrape_reddit_sub_v2(reddit_page, category, traceid, utc_now):
    logger.info(f"[{traceid}] Starting scrape v2 — subreddit: r/{reddit_page} | category: {category}")
    try:
        file_content = f'REDDIT SCRAPE TIME UTC:  {utc_now.strftime("%Y-%m-%d %H:%M:%S %Z")} \n'
        file_content += f'[CATEGORY] :: {category}\n'

        sub_url = get_sub_url(reddit_page)
        listing_url = f'{sub_url}/{category}/.json'

        logger.info(f"[{traceid}] Fetching subreddit listing (v2): {listing_url}")
        data = _fetch_json(listing_url, traceid)

        posts = data['data']['children']
        logger.info(f"[{traceid}] Found {len(posts)} posts in r/{reddit_page}/{category}")

        seen_urls = {}
        scraped_count = 0
        skipped_count = 0

        for seq, post in enumerate(posts):
            content = post['data']
            content_url = content['url'] + '.json'

            if content_url in seen_urls:
                logger.debug(f"[{traceid}] [{seq}] Skipping duplicate: {content_url}")
                skipped_count += 1
                continue
            seen_urls[content_url] = ''

            if 'https://www.reddit.com/r/' not in content_url:
                if content_url.startswith('/r/'):
                    content_url = 'https://www.reddit.com' + content_url
                    logger.debug(f"[{traceid}] [{seq}] Resolved relative URL: {content_url}")
                else:
                    logger.debug(f"[{traceid}] [{seq}] Skipping external URL: {content_url}")
                    skipped_count += 1
                    continue

            logger.debug(f"[{traceid}] [{seq}] Scraping post (v2): {content_url}")
            file_content += scrape_reddit_post_v2(content_url, traceid)
            scraped_count += 1
            time.sleep(1)

        logger.info(f"[{traceid}] Scrape v2 complete — scraped: {scraped_count} | skipped: {skipped_count}")

        reddit_download_path = os.path.join(MD_FILES, utc_now.strftime('%Y%m%d'))
        os.makedirs(reddit_download_path, exist_ok=True)
        reddit_file_name = f"reddit_scrape_v2_{category}_{traceid[:8]}_{utc_now.strftime('%Y%m%d_%H%M%S')}.md"
        reddit_file_location = os.path.join(reddit_download_path, reddit_file_name)

        with open(reddit_file_location, 'w', encoding='utf-8') as f:
            f.write(file_content)

        logger.info(f"[{traceid}] File saved: {reddit_file_location}")
        return reddit_file_location

    except Exception as ex:
        logger.exception(f"[{traceid}] Error scraping subreddit '{reddit_page}' (v2): {ex}")
        raise
