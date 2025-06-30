#%%
# Imports all core libraries for web requests, data handling, and file output.

import requests, csv
import pandas as pd
from datetime import date
from tqdm import tqdm
#%%
# Brings in project-specific helper functions.

from find_qid import find_qid_by_orcid
from find_qid import _api_get
#%%
# Defines a reusable function to extract selected sections from an ORCID profile (education, works, peer reviews).
# The output is structured and ready for mapping to Wikidata properties.

def fetch_orcid_sections(orcid_id: str) -> dict:
    headers = {"Accept": "application/json"}
    base_url = f"https://pub.orcid.org/v3.0/{orcid_id}"

    # def fetch_employment():
    #     url = f"{base_url}/employments"
    #     resp = requests.get(url, headers=headers)
    #     out = []
    #     if resp.ok:
    #         for group in resp.json().get("affiliation-group", []):
    #             for s in group.get("summaries", []):
    #                 emp = s.get("employment-summary")
    #                 if emp:
    #                     out.append(emp)
    #     return out[:5]

    # Retrieves education summaries from ORCID.
    def fetch_education():
        url = f"{base_url}/educations"
        resp = requests.get(url, headers=headers)
        out = []
        if resp.ok:
            for group in resp.json().get("affiliation-group", []):
                for s in group.get("summaries", []):
                    edu = s.get("education-summary")
                    if edu:
                        out.append(edu)
        return out

    # Fetches works (e.g. publications); only the top(x) version per entry is used.
    def fetch_works():
        url = f"{base_url}/works"
        resp = requests.get(url, headers=headers)
        out = []
        if resp.ok:
            for group in resp.json().get("group", []):
                work_summary = group.get("work-summary", [])
                if work_summary:
                    out.append(work_summary[0])  # only the first (representative) version
        return out[:5]

    # Collects peer review activity data from ORCID.
    def fetch_peer_reviews():
        url = f"{base_url}/peer-reviews"
        resp = requests.get(url, headers=headers)
        out = []
        if resp.ok:
            for group in resp.json().get("group", []):
                for subgroup in group.get("peer-review-group", []):
                    for summary in subgroup.get("peer-review-summary", []):
                        out.append(summary)
        return out

    # Returns selected sections as a dictionary, ready for further processing.
    return {
        # "Employment": fetch_employment(),
        "Education and qualification": fetch_education(),
        "Work": fetch_works(),
        "Peer Reviews": fetch_peer_reviews(),
    }

#%%
"""
Sorts a list of ORCID entries by their completion year in descending order.
Handles missing years gracefully by pushing them to the end.
"""

def sort_by_completion_year(entries, reverse=True):
    def extract_year(entry):
        # Extracts the year from a nested “completion-date” structure; defaults to 9999 if missing.
        return int(entry.get("completion-date", {}).get("year", {}).get("value") or 9999)
    # Sorts entries by extracted year, newest first (default).
    return sorted(entries, key=extract_year, reverse=reverse)
#%%
# Test call
# peer_list = sort_by_completion_year(data.get("Peer Reviews", []))
# review = peer_list[0] if peer_list else None

# print(review)
#%%
"""
Reads a pre-filtered CSV of ORCID entries and checks for each whether a corresponding Wikidata Q-ID already exists.
Rows with missing data are skipped.
"""

# Loads the input CSV and removes any rows with missing values.
csv_input_path = "../outputs/orcid_only.csv"
df = pd.read_csv(csv_input_path).dropna()
# df = df.head(15)

# Iterates through all non-empty rows in the DataFrame.
for _, r in df.iterrows():
    # name = str(r["Name"]).strip()
    # Extracts and cleans the ORCID ID from each row.
    orcid = str(r["orcid"]).strip() if pd.notna(r["orcid"]) else ""
    print(f"Processing {orcid}")
    # Checks if the ORCID is already linked to a Wikidata Q-ID.
    qid = find_qid_by_orcid(orcid)
#%%
"""
This function generates Wikidata QuickStatements from ORCID data, structured by section (Education → P69, Works → P800, Peer Reviews → P4032).
It writes each block with proper source and date qualifiers.
"""

def export_orcid_qs(data_dict: dict, output_path: str, limits: dict):
    today = date.today().isoformat()
    today_wd = f'+{today}T00:00:00Z/11'

# with open(output_path, mode='w', newline='', encoding='utf-8') as f:
    # writer = csv.writer(f, delimiter='|', quoting=csv.QUOTE_MINIMAL)
    # writer.writerow(['ID', 'P', 'Value', 'Qualifier_P', 'Qualifier_V', 'S854', 'S813'])

    # Opens output file for writing QuickStatements
    with open(output_path, mode='w', encoding='utf-8') as f:
        # Iterates through all ORCID profiles
        # for orcid_id, sections in data_dict.items():
        for orcid_id, sections in tqdm(data_dict.items(), desc="Exportiere QS-Zeilen"):
            source_url = f"https://orcid.org/{orcid_id}"

            ####################################################################
            # Noch keine QIDs, da die Einträge noch nicht existieren
            ####################################################################
            qids = False # --> Set to on True when the new entries have been imported
            ####################################################################
            QID = "None"
            # Currently unused. future logic to switch to the edit mode
            if qids == True:
                QID = qid
                qid = find_qid_by_orcid(orcid_id)
                if not qid:
                    print(f"[warn] Keine QID für ORCID {orcid_id} gefunden – übersprungen")
                    continue
                f.write(f"{qid}\n")
            ####################################################################

            # EMPLOYMENT → P108
            # for emp in sections.get("Employment", [])[:limits.get("Employment", 1)]:
            #     if not isinstance(emp, dict):
            #         continue
            #     org = emp.get('organization', {}).get('name')
            #     start = (emp.get('start-date') or {}).get('year', {}).get('value') or {}
            #     start_fmt = f'+{start}-00-00T00:00:00Z/9' if start else ''
            #     if org:
            #         row = ['CREATE', 'P108', org]
            #         row += ['P580', start_fmt] if start_fmt else ['', '']
            #         row += ['S854', source_url, 'S813', today_wd]
            #         writer.writerow(row)

            # EDUCATION → P69
            # Iterates over education entries.
            # for edu in sections.get("Education and qualification", [])[:limits.get("Education", 0)]:
            for edu in tqdm(sections.get("Education", [])[:limits.get("Education", 0)], desc=f"{orcid_id} - Education", leave=True):
                if not isinstance(edu, dict):
                    continue

                inst = edu.get('organization', {}).get('name')
                start = (edu.get('start-date') or {}).get('year', {}).get('value')
                start_fmt = f'+{start}-00-00T00:00:00Z/9' if start else ''
                if inst:
                    """ OLD
                    row = ['CREATE', 'P69', inst]
                    row += ['P580', start_fmt] if start_fmt else ['', '']
                    row += ['S854', source_url, 'S813', today_wd]
                    writer.writerow(row)
                    """
                    ################################################################
                    # NEW:
                    # f.write("CREATE\n")
                    f.write(f"{QID}\n")
                    line = f'LAST|P69|"{inst}"'
                    if start_fmt:
                        line += f'|P580|{start_fmt}'
                    line += f'|S854|"{source_url}"|S813|{today_wd}\n'
                    f.write(line)

            # WORK → P800
            # Iterates over work entries.
            # for work in sections.get("Work", [])[:limits.get("Work", 0)]:
            for work in tqdm(sections.get("Work", [])[:limits.get("Work", 0)], desc=f"{orcid_id} - Work", leave=True):
                if not isinstance(work, dict):
                    continue

                title = work.get("title", {}).get("title", {}).get("value")
                if title:
                    """ OLD:
                    row = ['CREATE', 'P800', title, '', '', 'S854', source_url, 'S813', today_wd]
                    writer.writerow(row)
                    """
                    ################################################################
                    # NEU:
                    # f.write("CREATE\n")
                    f.write(f"{QID}\n")
                    line = f'LAST|P800|"{title}"|S854|"{source_url}"|S813|{today_wd}\n'
                    f.write(line)

            # PEER REVIEW → P4032
            peer_list = sort_by_completion_year(sections.get("Peer Reviews", []))[:limits.get("Peer", 0)]
            # Iterates over peer review entries.
            # for review in peer_list:
            for review in tqdm(peer_list, desc=f"{orcid_id} - Peer Review", leave=True):
                if not isinstance(review, dict):
                    continue

                org = review.get("convening-organization", {}).get("name")
                issn = review.get("review-group-id", "")

                if issn.startswith("issn:"):
                    issn = issn.replace("issn:", "")
                else:
                    issn = ""

                if org:
                    """ OLD:
                    row = ['CREATE', 'P4032', org]
                    if issn:
                        row += ['P236', issn]
                    else:
                        row += ['', '']
                    row += ['S854', source_url, 'S813', today_wd]
                    writer.writerow(row)
                    """
                    ################################################################
                    # NEU:
                    # f.write("CREATE\n")
                    f.write(f"{QID}\n")
                    line = f'LAST|P4032|"{org}"'
                    if issn:
                        line += f'|P236|"{issn}"'
                    line += f'|S854|"{source_url}"|S813|{today_wd}\n'
                    f.write(line)
#%%
# Test call
# orcid_id = "0000-0002-1481-2996"
# data = fetch_orcid_sections(orcid_id)

# print(data)
#%%
"""
This block processes all ORCID entries in the input DataFrame, fetches detailed section data for each, and calls the export function to create a
structured QS output file. Limits are set to control how many items per section are exported.
"""

# Test
# orcid_ids = ["0000-0002-1481-2996", "0000-0002-9421-8582"]

# Extracts the ORCID column from the DataFrame and collects structured ORCID data for each ID.
orcid_ids = df["orcid"]
orcid_data = {oid: fetch_orcid_sections(oid) for oid in orcid_ids}

# Defines how many entries per section to export per person.
limits = {
    #"Employment": 1,
    "Education": 5,
    "Work": 5,
    "Peer": 5
}
# print(orcid_data)

# Generates and writes QuickStatements to output file using previously collected data and limits.
export_orcid_qs(orcid_data, "../outputs/qs_further_items_output.csv", limits)
#%%
