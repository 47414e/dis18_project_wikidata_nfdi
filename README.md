# DIS18 Project WikiData NFDI
Hochschule: TH-Köln 
Modul: DIS18 Projekt 1
Thema: WikiData NFDI

## Project Description:
Integration of NFDI4Microbiota Researchers into Wikidata

As part of this project, we were provided with an Excel spreadsheet containing a list of researchers and their respective research institutions in the context of NFDI4Microbiota. The aim of the project is to systematically import these datasets into Wikidata.

The names of the researchers are initially cross-referenced with existing sources such as ORCID, Scholia, or the websites of the participating projects (e.g., NFDI4Microbiota, base4NFDI). This process checks whether a Wikidata entry already exists for each individual. Existing entries are disregarded in this project; the focus is solely on identifying and creating new entries.

For each new individual, their ORCID iD is retrieved from the ORCID directory, if available, and linked to the corresponding Wikidata entry. The ORCID iD is stored in Wikidata as a distinct identifier with the appropriate source citation.

Already existing entities that can be associated with the person—such as research institutions or project involvements—are linked to the new person entry as so-called “sub-objects.” The entry begins with basic information (name, institution, identifiers) and is supplemented with additional details if the project duration permits.

Code Overview
To support the described process, several scripts and Jupyter notebooks were developed. These automate the retrieval and preparation of relevant data, particularly regarding ORCID iDs and existing Wikidata entries:

ORCID Lookup: A script searches for a matching ORCID iD for each person.

Wikidata Check: For known ORCID iDs, the script checks whether a corresponding Wikidata entry already exists.

QID Retrieval: If a Wikidata entry is found, its unique identifier (QID) is retrieved.

Data Preparation: The collected information is compiled into a structured CSV file, which can be used for importing into Wikidata—e.g., via QuickStatements.

Supplementary Modules: Additional notebooks enable the completion of missing details or the linking to existing entities, such as research institutions.

The codebase is modular and can be adapted to other projects with similar requirements.
It is designed for extensibility and can be expanded as needed.

