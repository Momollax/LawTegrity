
import requests
from dotenv import load_dotenv
from utils.rate_limiter import RateLimiter
import os
load_dotenv()
rateLimit = os.getenv('RATE_LIMIT')

rate_limiter = RateLimiter(max_requests_per_second=float(rateLimit))
load_dotenv()
from utils.decorators import auto_refresh_token
@auto_refresh_token
def get_law_content(access_token, text_id):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    url = os.getenv('API_BASE_URL') + '/consult/legiPart'

    payload = {
        "textId": text_id
    }

    response = requests.post(url, headers=headers, json=payload)
    rate_limiter.wait()
    response.raise_for_status()
    return response.json()