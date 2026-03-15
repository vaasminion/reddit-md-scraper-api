from functools import wraps

from flask import request, jsonify

from config import API_KEY
from logger import logger


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not API_KEY:
            # API_KEY not configured — open access (local dev)
            return f(*args, **kwargs)
        key = request.headers.get('X-API-Key')
        if not key:
            logger.warning("Rejected request — missing X-API-Key header")
            return {"error": "Missing API key"}, 401
        if key != API_KEY:
            logger.warning("Rejected request — invalid API key")
            return {"error": "Invalid API key"}, 403
        return f(*args, **kwargs)
    return decorated
