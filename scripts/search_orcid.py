#%%
# Necessary imports
import argparse, csv, logging, time, urllib.parse
import orjson, pandas as pd, requests
from __future__ import annotations
from pathlib import Path
from SPARQLWrapper import SPARQLWrapper, JSON
#%%
# Base URL for ORCID API v3.0
ORCID_BASE = "https://pub.orcid.org/v3.0"

# HTTP header to specify the desired response format (JSON)
HEADERS    = {"Accept": "application/json"}

# File paths
BASE_DIR = Path.cwd()
DATA_FILE  = BASE_DIR / "import" / "NFDI4Microbiota_staff_input.xlsx"
OUT_FILE   = BASE_DIR / "import" / "input_with_orcid.csv"

# Seconds between API calls
RATE_SLEEP = 0.25
#%%
"""
Performs an HTTP GET request to the specified URL and returns the response as JSON.
Up to three attempts are made if an error occurs (e.g., connection error, timeout, HTTP error).
The response is decoded using `orjson`.
"""

def _get_json(url: str) -> dict:
    # Retry up to three times on errors
    for attempt in range(3):
        try:
            # Perform HTTP GET with set headers and timeout
            r = requests.get(url, headers=HEADERS, timeout=20)

            # Raises an exception for HTTP error codes (4xx, 5xx)
            r.raise_for_status()

            # Decode and return JSON response
            return orjson.loads(r.content)

        # On any network/HTTP issues: log and retry
        except requests.exceptions.RequestException as exc:
            logging.warning("ORCID call failed (%s/3): %s", attempt + 1, exc)
            time.sleep(1)

    # After three failed attempts: return empty dict
    return {}
#%%
"""
Function that searches for an ORCID iD based on given name and optional organization.

Strategy:
    1. Search with given name and family name.
    2. If an organization (`org`) is provided, perform a second attempt with an affiliation filter.

The function returns the first found ORCID iD or `None` if no matches are found.
"""

def orcid_search(given: str, family: str, org: str | None = None, debug: bool = False) -> str | None:
    # Without a family name, no query is possible – ORCID requires given and family names
    if not family:
        return None

    # Build base query: given name + family name
    base_q = f'given-names:"{given}"+AND+family-name:"{family}"'
    queries = [base_q]

    # If organization is given, extend the search query
    if org:
        queries.append(f'{base_q} AND affiliation-org-name:"{org}"')

    # Try each defined query in sequence
    for q in queries:
        # Replace spaces with '+' for ORCID-compatible syntax
        q_plus = q.replace(' ', '+')

        # URI-encoding: '+' must not be escaped, nor ':' and '"'
        encoded_q = urllib.parse.quote(q_plus, safe=':"+')

        # Compose the full API URL with the search term
        url = f"{ORCID_BASE}/expanded-search/?q={encoded_q}&rows=5"

        # Optional: show the used query in plain text
        if debug:
            print("🚀 Query:", urllib.parse.unquote(url))

        # Send API request and load JSON data
        data = _get_json(url)

        # Optional: inspect raw structure of the response
        if debug:
            print("  ↳ raw keys:", list(data.keys()))

        # Extract results – ORCID sometimes uses different keys
        hits = data.get("result") or data.get("expanded-result")

        # Optional: show number of hits found
        if debug:
            print("  ↳ result count:", len(hits or []))

        # Wait to reduce API load
        time.sleep(RATE_SLEEP)

        # Return ORCID iD of the first hit
        if hits:
            return hits[0]["orcid-id"]

    # No match → return None
    return None

#%%
"""
Performs a SPARQL query on Wikidata to retrieve the ORCID iD of a person based on their name.
The query performs a case-insensitive exact label match (rdfs:label) in Wikidata and returns the associated ORCID iD (P496).
"""

def scholia_orcid(full_name: str) -> str | None:
    # Initialize SPARQL query via the Wikidata endpoint
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    # Set response format to JSON
    sparql.setReturnFormat(JSON)

    # Define SPARQL query: search label case-insensitively
    sparql.setQuery(f'''
        SELECT ?orcid WHERE {{
          ?person wdt:P496 ?orcid ;
                  rdfs:label ?lab .
          FILTER(LCASE(STR(?lab)) = "{full_name.lower()}")
        }} LIMIT 1''')

    try:
        # Execute query and extract result
        res = sparql.query().convert()["results"]["bindings"]

        # Return ORCID iD if a hit is found
        return res[0]["orcid"]["value"] if res else None

    except Exception as exc:
        # SPARQL execution error → debug log + None
        logging.debug("SPARQL error for %s: %s", full_name, exc)
        return None

#%%
"""
Performs ORCID enrichment for an Excel list of people.

For each person (name + institution), attempts to find a matching ORCID iD via the ORCID API or Wikidata.
The results are exported to a CSV file.
"""

# limit (int | None, optional): Number of people to process (for testing or debugging).
DEFAULT_LIMIT = 5

def run(limit: int | None = DEFAULT_LIMIT):
    logging.info("📥  Loading staff list …")

    # Read input file (Excel)
    df = pd.read_excel(DATA_FILE)

    # Result rows for CSV output
    rows = []

    for idx, r in enumerate(df.itertuples(index=False), start=1):

        # Stop processing after 'limit' entries
        if limit and idx > limit:
            break

        # Split given and family names
        parts = str(r.Name).strip().split()
        given  = parts[0]
        family = " ".join(parts[1:])

        logging.info("▶ [%s/%s] %s", idx, len(df), r.Name)

        # ORCID search via official API, optionally with institution
        orcid_id = orcid_search(given, family, r.Institution)

        # Fallback: ORCID search via Wikidata (SPARQL)
        if not orcid_id:
            orcid_id = scholia_orcid(r.Name)

        # Add entry to result list
        rows.append({
            "Institution":  r.Institution,
            "Name":         r.Name,
            "ORCID":        orcid_id or "",
            "ORCID-Link":   f"https://orcid.org/{orcid_id}" if orcid_id else ""
        })

    logging.info("💾  Writing %s", OUT_FILE)

    # Write results to CSV file
    pd.DataFrame(rows).to_csv(OUT_FILE, index=False, quoting=csv.QUOTE_ALL)

    logging.info("✅  Done – %s rows", len(rows))

#%%
if __name__ == "__main__":

    # Configure logging format and level
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, help="Process only N rows")

    # Read arguments from sys.argv (ignore unknown arguments)
    args, _ = parser.parse_known_args(sys.argv[1:])

    # Start main process with the specified limit
    run(args.limit)

#%%
# Test call
# orcid1 = orcid_search("Konrad", "Förstner", debug=True)
# print("ORCID1:", orcid1)