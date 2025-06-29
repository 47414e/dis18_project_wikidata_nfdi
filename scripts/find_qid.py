from typing import Optional, Dict
from functools import lru_cache
import requests, time

# Base endpoint of the MediaWiki API (Wikidata)
API_ENDPOINT = "https://www.wikidata.org/w/api.php"

# HTTP headers for API access, especially a custom User-Agent (required by API guidelines)
HEADERS = {"User-Agent": "NFDI4Microbiota-QS-Generator/2.0 (info@example.com)"}

# Maximum number of retry attempts on errors (e.g., rate limit, timeout)
MAX_RETRIES = 3

# Wait time in seconds between retry attempts (backoff time)
BACKOFF_SECS = 3

"""
Performs a GET request to the Wikidata API with error handling and automatic retries.
"""

def _api_get(params: Dict) -> Dict:  # API
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Perform GET request with headers and timeout
            r = requests.get(API_ENDPOINT, params=params, headers=HEADERS, timeout=25)

            # Raise exception on HTTP errors (e.g., 403, 500)
            r.raise_for_status()

            # Decode and return JSON response
            return r.json()

        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            # On timeout or connection errors: wait (linearly increasing) and retry
            wait = BACKOFF_SECS * attempt
            print(f"[warn] API timeout – attempt {attempt}/{MAX_RETRIES}, waiting {wait}s …")
            time.sleep(wait)

        except requests.exceptions.HTTPError as e:
            # On HTTP errors (e.g., 403, 500): abort and do not retry
            print(f"[error] API HTTP {e.response.status_code}: {e.response.reason}")
            break
    # Return empty dict if all attempts fail
    return {}

"""
Finds the Wikidata QID for a given ORCID ID using the 'haswbstatement' search function.
"""

# Enable caching to avoid duplicate API requests
@lru_cache(maxsize=None)
def find_qid_by_orcid(orcid: str) -> Optional[str]:
    # Immediately abort on empty input
    if not orcid:
        return None
    # Build special search query (CirrusSearch for ORCID property P496)
    query = f'haswbstatement:P496="{orcid}"'

    # Send request to the Wikidata API
    data =
