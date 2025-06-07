from typing import Optional, Dict
from functools import lru_cache
import requests, time, os
import pandas as pd

# Basis-Endpunkt der MediaWiki API (Wikidata)
API_ENDPOINT = "https://www.wikidata.org/w/api.php"

# HTTP-Header für API-Zugriffe, insbesondere ein benutzerdefinierter User-Agent (erforderlich laut API-Richtlinien)
HEADERS = {"User-Agent": "NFDI4Microbiota-QS-Generator/2.0 (info@example.com)"}

# Maximale Anzahl an Wiederholungsversuchen bei Fehlern (z. B. Rate-Limit, Timeout)
MAX_RETRIES = 3

# Wartezeit in Sekunden zwischen Wiederholungsversuchen (Back-off-Zeit)
BACKOFF_SECS = 3

"""
Führt eine GET-Anfrage an die Wikidata API aus, mit Fehlerbehandlung und automatischer Wiederholung.
"""

def _api_get(params: Dict) -> Dict:  # API
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Führe GET-Anfrage aus, mit Header und Timeout
            r = requests.get(API_ENDPOINT, params=params, headers=HEADERS, timeout=25)

            # Löst eine Ausnahme bei HTTP-Fehlern aus (z. B. 403, 500)
            r.raise_for_status()

            # JSON-Antwort dekodieren und zurückgeben
            return r.json()

        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            # Bei Timeout oder Verbindungsfehler: warte (linear steigend) und versuche es erneut
            wait = BACKOFF_SECS * attempt
            print(f"[warn] API timeout – Versuch {attempt}/{MAX_RETRIES}, warte {wait}s …")
            time.sleep(wait)

        except requests.exceptions.HTTPError as e:
            # Bei HTTP-Fehlern (z. B. 403, 500): abbrechen, nicht erneut versuchen
            print(f"[error] API HTTP {e.response.status_code}: {e.response.reason}")
            break
    # Rückgabe bei Fehlschlag aller Versuche: leeres Dictionary
    return {}

"""
Findet die Wikidata-QID zu einer gegebenen ORCID-ID mithilfe der Suchfunktion 'haswbstatement'.
"""

# Aktiviere Caching, um doppelte API-Anfragen zu vermeiden
@lru_cache(maxsize=None)
def find_qid_by_orcid(orcid: str) -> Optional[str]:
    # Leere Eingabe sofort abbrechen
    if not orcid:
        return None
    # Baue die spezielle Suchanfrage (CirrusSearch über ORCID property P496)
    query = f'haswbstatement:P496="{orcid}"'

    # Anfrage an Wikidata-API stellen
    data = _api_get(
        {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": 1,
            "format": "json"
        }
    )
    try:
        # Extrahiere QID aus dem ersten Suchtreffer (z. B. "Q12345")
        return data["query"]["search"][0]["title"]
    except (KeyError, IndexError):
        # Kein Treffer gefunden oder Antwort unerwartet → gib None zurück
        return None