import os
import requests
from dotenv import load_dotenv
from utils.rate_limiter import RateLimiter

load_dotenv()
rateLimit = os.getenv('RATE_LIMIT')

rate_limiter = RateLimiter(max_requests_per_second=float(rateLimit))
load_dotenv()

def ping_api(access_token):
    """
    Ping the Legifrance API to check access
    """
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    ping_url = os.getenv('PING_URL')

    response = requests.get(ping_url, headers=headers)
    rate_limiter.wait()
    response.raise_for_status()
    return response.text
