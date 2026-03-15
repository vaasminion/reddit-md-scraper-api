import urllib.request
import json
import time
import os

from config import USER_AGENT, MD_FILES
from logger import logger


def get_comments(comments, depth=0):
    result = ""
    for comment in comments:
        comment_data = comment['data']
        author = comment_data.get('author', '[deleted]')
        body = comment_data.get('body', '')
        indent = "--" * depth

        if 'RemindMeBot' in body or 'RemindMeBot' in author:
            result += '\n\n'
        else:
            result += f"{indent}👤 {author}: {body}\n\n"

        replies = comment_data.get('replies', '')
        if replies and isinstance(replies, dict):
            nested_comments = replies['data']['children']
            result += get_comments(nested_comments, depth + 1)

    return result


def get_sub_url(reddit_sub_name):
    return f'https://www.reddit.com/r/{reddit_sub_name}/'


def scrape_RedditPost(url):
    logger.debug(f"Fetching post: {url}")
    req = urllib.request.Request(url)
    req.add_header('User-Agent', USER_AGENT)
    req.add_header('Accept', 'application/json')
    with urllib.request.urlopen(req, timeout=15) as response:
        commentdata = json.loads(response.read().decode('utf-8'))
    time.sleep(2)
    result = ''

    for userpost in commentdata[0]['data']['children']:
        author_name = userpost['data']['author']
        post_content = userpost['data']['selftext']
        title = userpost['data']['title']

        logger.debug(f"Post scraped — title: '{title}' | author: {author_name}")

        result += f'[TITLE] :: {title} \n'
        result += f'[AUTHOR_NAME] :: {author_name} \n'
        result += f'[URL] :: {url}\n'
        result += f'[BODY] :: {post_content} \n'

    comment_list = commentdata[1]['data']['children']
    logger.debug(f"Parsing {len(comment_list)} top-level comments for: {url}")
    comments = get_comments(comment_list)
    result += f'[COMMENTS] :: {comments} \n'
    return result


def scrape_RedditSub(reddit_page, category, traceid, utc_now):
    logger.info(f"[{traceid}] Starting scrape — subreddit: r/{reddit_page} | category: {category}")
    try:
        fileContent = f'REDDIT SCRAPE TIME UTC:  {utc_now.strftime("%Y-%m-%d %H:%M:%S %Z")} \n'
        sub_url = get_sub_url(reddit_page)
        SEEN_URL = {}

        url = f'{sub_url}/{category}/.json'
        req = urllib.request.Request(url)
        fileContent += f'[CATEGORY] :: {category}\n'
        req.add_header('User-Agent', USER_AGENT)
        req.add_header('Accept', 'application/json')
        req.add_header("Accept-Language", "en-US,en;q=0.9")
        req.add_header("Accept-Encoding", "identity")
        req.add_header("Connection", "keep-alive")

        logger.info(f"[{traceid}] Fetching subreddit listing: {url}")
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))

        posts = data['data']['children']
        logger.info(f"[{traceid}] Found {len(posts)} posts in r/{reddit_page}/{category}")

        scraped_count = 0
        skipped_count = 0

        for seq, i in enumerate(posts):
            content = i["data"]
            content_url = content["url"] + '.json'

            if content_url in SEEN_URL:
                logger.debug(f"[{traceid}] [{seq}] Skipping duplicate: {content_url}")
                skipped_count += 1
                continue
            SEEN_URL[content_url] = ''

            if 'https://www.reddit.com/r/' not in content_url:
                if '/r/' == content_url[0:3]:
                    content_url = 'https://www.reddit.com' + content_url
                    logger.debug(f"[{traceid}] [{seq}] Resolved relative URL: {content_url}")
                else:
                    logger.debug(f"[{traceid}] [{seq}] Skipping external URL: {content_url}")
                    skipped_count += 1
                    continue

            logger.debug(f"[{traceid}] [{seq}] Scraping post: {content_url}")
            fileContent += scrape_RedditPost(content_url)
            scraped_count += 1
            time.sleep(1)

        logger.info(f"[{traceid}] Scrape complete — scraped: {scraped_count} | skipped: {skipped_count}")

        reddit_download_path = os.path.join(MD_FILES, utc_now.strftime('%Y%m%d'))
        os.makedirs(reddit_download_path, exist_ok=True)
        reddit_file_name = f"reddit_scrape_{category}_{traceid[:8]}_{utc_now.strftime('%Y%m%d_%H%M%S')}.md"
        reddit_file_location = os.path.join(reddit_download_path, reddit_file_name)

        with open(reddit_file_location, 'w', encoding='utf-8') as f:
            f.write(fileContent)

        logger.info(f"[{traceid}] File saved: {reddit_file_location}")
        return reddit_file_location

    except Exception as ex:
        logger.exception(f"Error scraping subreddit '{reddit_page}' [{traceid}]: {ex}")
        raise ex
