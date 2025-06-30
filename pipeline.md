## Data Pipeline

### 🔄 ORCID Lookup and QS Generation

#### 📁 1. Input Data

| File                                  | Description                                                                                                       |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| NFDI4Microbiota\_staff\_original.xlsx | Original raw data (unmodified)                                                                                    |
| NFDI4Microbiota\_staff\_input.xlsx    | Preprocessed list of selected individuals for further processing; formatting cleaned and unnecessary data removed |

---

### 🔍 2. ORCID Lookup

**Notebook:** `search_orcid.ipynb`
**Functions:** `orcid_search(...)` + `scholia_orcid(...)`
→ Automates enrichment with ORCID iD

#### 🔧 Steps:

1. Read input Excel file (`staff_input.xlsx`)
2. Iterate over names & institutions
3. Search for ORCID via:

   * ORCID Public API
   * Wikidata (SPARQL)
4. Merge results
5. Export to `input_with_orcid.csv`

**Result:**
✅ File: `input_with_orcid.csv` → includes name, institution, ORCID, and ORCID link

---

### 📝 3. QuickStatements Generation

**Notebook:** `qs_csv.ipynb`
**Function:** `file_to_qs(...)`

#### 🔧 Steps:

1. Read `input_with_orcid.csv`
2. Check for existing entries in Wikidata (via ORCID or name)
3. Resolve institution names to Q-IDs
4. Generate QS lines for:

   * `P31:Q5` (instance of human)
   * `P496` (ORCID)
   * `P108` (employer / institution)
   * `S854` (source URL)
5. Export as `quickstatements.csv`

**Result:**
✅ File: `quickstatements.csv` → ready to import via Wikidata QuickStatements tool

---

### ➕ 4. Further QuickStatements

**Notebook:** `qs_further_items_outputs.ipynb`
**Function:** `export_orcid_qs(...)`

#### 🔧 Steps:

1. Read `orcid_only.csv`
2. No need to check for existing entries – ORCID is already included
3. Resolve Q-IDs using ORCID
4. Generate QS lines for:

   * `P108` (employment)
   * `P69` (education)
   * `P800` (notable work)
   * `P4032` (peer review)
5. Export as `qs_further_items_output.csv`

**Result:**
✅ File: `qs_further_items_output.csv` → ready to import via Wikidata QuickStatements tool

