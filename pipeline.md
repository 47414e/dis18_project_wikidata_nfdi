## Datenpipeline

### 🔄 ORCID-Suche und QS-Erzeugung
#### 📁 1. Eingangsdaten

| Datei                               | Beschreibung                                                                                                        |
|-------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| NFDI4Microbiota_staff_original.xlsx | Ursprüngliche Rohdaten (unbearbeitet)                                                                               |
| NFDI4Microbiota_staff_input.xlsx    | Vorausgewählte Personenliste zur Verarbeitung vorbereitet; Formatierunge und nicht benöitgte Informationen entfernt |

### 🔍 2. ORCID-Suche

Notebook: search_orcid.ipynb\
Funktion: orcid_search(...) + scholia_orcid(...)\
→ Automatisierte Anreicherung um ORCID-ID

#### 🔧 Schritte:
1. Einlesen der Excel-Datei (staff_input.xlsx)
2. Iteration über Namen & Institutionen 
3. Suche nach ORCID via:
   * ORCID Public API
   * Wikidata (SPARQL)
4. Zusammenführen der Ergebnisse
5. Export als input_with_orcid.csv

Ergebnis:
✅ Datei: input_with_orcid.csv → enthält Name, Institution, ORCID, ORCID-Link

### 3. Erstellung der QuickStatements

Notebook: qs_csv.ipynb
Funktion: file_to_qs(...)

#### 🔧 Schritte:
1. Einlesen von input_with_orcid.csv 
2. Prüfung auf bestehende Personen in Wikidata (via ORCID oder Name)
3. Auflösung der Institutionen zu Q-IDs 
4. QS-Zeilen generieren für:
   * P31:Q5 (instance of human)
   * P496 (ORCID)
   * P108 (institution)
   * S854 (source URL)
5. Export als: quickstatements.csv

Ergebnis:
✅ Datei: quickstatements.csv → direkt importierbar via Wikidata QuickStatements Tool

### 4. Erstellung weitere QuickStatements

Notebook: qs_further_items_outputs.ipynb
Funktion: export_orcid_qs(...)

#### 🔧 Schritte:
1. Einlesen von orcid_only.csv 
2. Prüfung auf bestehende Personen in Wikidata (via ORCID oder Name) nicht notwendig, da bereits in die orcid mitgegeben wird
3. Auflösung der Q-IDs über ORCID 
4. QS-Zeilen generieren für:
   * EMPLOYMENT → P108
   * EDUCATION → P69
   * WORK → P800
   * PEER REVIEW → P4032
5. Export als: qs_further_items_output.csv

Ergebnis:
✅ Datei: qs_further_items_output.csv → direkt importierbar via Wikidata QuickStatements Tool