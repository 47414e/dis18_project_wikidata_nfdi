#%%
# Imports all core libraries for web requests, data handling, and file output.

import csv, time, os, re
import pandas as pd
from typing import Optional, Dict
from functools import lru_cache  # CACHE
#%%
# Brings in project-specific helper functions.

from find_qid import find_qid_by_orcid
from find_qid import _api_get
#%%
"""
Searches for the Wikidata QID of a given label (name), optionally language-specific.
"""

@lru_cache(maxsize=None)  # API/cache
def find_qid_by_name(name: str, lang: str = "en") -> Optional[str]:
    # Abort directly if input is empty
    if not name:
        return None

    # Send API request to wbsearchentities endpoint (Wikidata search)
    data = _api_get(
        {
            "action": "wbsearchentities",
            "search": name,
            "language": lang,
            "type": "item",
            "limit": 1,
            "format": "json"
        }
    )
    try:
        # Return the Q-ID of the first result (e.g. "Q123456")
        return data["search"][0]["id"]
    except (KeyError, IndexError):
        # No result or incomplete response → return None
        return None
#%%
"""
Searches for a Wikidata QID for an institution by its label.
Results are cached locally.
"""

# Simple cache: institution label → QID (or None if not found)
inst_cache: Dict[str, Optional[str]] = {}

def find_qid_by_institution_label(label: str) -> Optional[str]:  # API
    # Abort if no input
    if not label:
        return None

    # Return from cache if already present
    if label in inst_cache:
        return inst_cache[label]

    # Search Wikidata by label – first in English, then in German
    for lang in ("en", "de"):
        data = _api_get({
            "action": "wbsearchentities", "search": label, "language": lang,
            "type": "item", "limit": 1, "format": "json"})

        # If match found → extract and cache QID
        if data.get("search"):
            qid = data["search"][0]["id"]
            inst_cache[label] = qid

            # Optional info output if German label was used
            if lang == "de":
                print(f"[info] Institution '{label}' found via German label → {qid}")
            return qid

    # No match in either language → cache with None
    inst_cache[label] = None
    return None
#%%
"""
This function generates QuickStatements for creating new person entries in Wikidata based on an enriched input file.
Existing persons are skipped, while new ones are added with label, ORCID, source, and institution.
"""

def file_to_qs(infile: str, outfile: str) -> None:
    # Determine file extension (xls/xlsx or csv)
    ext = os.path.splitext(infile)[1].lower()

    # Read input file depending on format
    df = pd.read_excel(infile) if ext in {".xlsx", ".xls"} else pd.read_csv(infile)

    # Check if all required columns are present
    required = {"Name", "Institution", "ORCID", "ORCID-Link"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")

    # Initialize result list and deduplication tracker
    rows = []
    processed = set()

    # Iterate through all rows of input file
    for _, r in df.iterrows():
        name = str(r["Name"]).strip()

        # If ORCID is NaN, treat it as empty string
        orcid = str(r["ORCID"]).strip() if pd.notna(r["ORCID"]) else ""

        # Deduplicate by name + ORCID (lowercased)
        key = (name.lower(), orcid)
        if key in processed:
            continue
        processed.add(key)

        # Prepare institution and URL
        inst_label = str(r["Institution"]).strip()
        url = r["ORCID-Link"] if pd.notna(r["ORCID-Link"]) else ""

        # Check if person already exists (via ORCID or name)
        qid = find_qid_by_orcid(orcid) or find_qid_by_name(name)
        if qid:
            print(f"[skip] {name} already exists as {qid}")
            continue

        # Try to find institution QID
        inst_qid = find_qid_by_institution_label(inst_label)
        if not inst_qid:
            print(f"[warn] Institution '{inst_label}' not found ⇒ skipped")
            continue

        # Build QuickStatements row
        rows.append({
            "qid": "CREATE",
            "Len": name,
            "P31": "Q5",          # instance of → human
            "P496": orcid,        # ORCID
            "S854": url,          # source (URL)
            "P108": inst_qid,     # employer/affiliation
        })

        # Short pause to avoid overloading the API
        time.sleep(0.1)

    # If no new rows → skip export
    if not rows:
        print("No new items – nothing exported.")
        return

    #####################################################################
    # NEW: Write the QuickStatements-File in a CSV-File
    """field_order = ["qid", "Len", "P31", "P496", "S854", "P108"]
    with open(outfile, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=field_order)
        writer.writeheader()
        writer.writerows(rows)"""

    # NEW: Write the QuickStatements-File in a CSV-File
    with open(outfile, "w", encoding="utf-8") as f:
        for r in rows:
            f.write("CREATE\n")
            f.write(f'LAST|Len|"{r["Len"]}"\n')
            f.write("LAST|P31|Q5\n")
            if r["P496"]:
                f.write(f'LAST|P496|"{r["P496"]}"|S854|"{r["S854"]}"\n')
            f.write(f"LAST|P108|{r['P108']}\n\n")
    #####################################################################

    # Success message with row count
    print(f"✓ {len(rows)} QuickStatements rows → {outfile}")

#%%
# Path to input file with people, institutions, and ORCID info
csv_input_path = "../outputs/input_with_orcid.csv"

# Path to output file for generated QuickStatements in CSV format
csv_output_path = "../outputs/qs_main_items.csv"

# Start processing: check existing QIDs and create new QS rows
file_to_qs(csv_input_path, csv_output_path)
#%%
#####################################################################
""" OLD:
df = pd.read_csv(csv_output_path)

# Export only the ORCID column for further processing
orcid_column = df[["P496"]].rename(columns={"P496": "orcid"})
orcid_column.to_csv("../outputs/orcid_only.csv", index=False)

print("✓ ORCID list was exported")
"""
#####################################################################
#####################################################################
# NEW:
#####################################################################
# Load the QuickStatements CSV file
df_main = pd.read_csv(csv_output_path)

# Filter only the rows that contain an ORCID (P496)
orcid_lines = df_main[df_main['CREATE'].str.contains("P496", na=False)]

# Extract ORCID values using a regular expression
# The pattern looks for: P496|"0000-0001-2345-6789"
orcids = orcid_lines['CREATE'].apply(lambda x: re.search(r'P496\|\"([\d\-X]+)\"', x))
orcid_values = orcids.dropna().apply(lambda m: m.group(1))

# Convert the extracted values into a new DataFrame
orcid_df = pd.DataFrame(orcid_values, columns=["orcid"])

# Export the result to CSV
orcid_df.to_csv("../outputs/orcid_only.csv", index=False)
print("✓ ORCID list exported successfully.")
#####################################################################
#%%
# Test call (commented out)
# orcid = "0000-0002-1481-2996"
# data = fetch_orcid_sections(orcid)
# print(data)