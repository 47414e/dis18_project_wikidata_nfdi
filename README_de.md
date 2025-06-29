# DIS18 Project WikiData NFDI
Hochschule: TH-Köln 
Modul: DIS18 Projekt 1
Thema: WikiData NFDI

## Projektbeschreibung: 
Integration von NFDI4Microbiota-Forschenden in Wikidata

Im Rahmen dieses Projekts wurde uns eine Excel-Tabelle mit einer Liste von Forscherinnen und Forschern sowie den jeweils zugehörigen Forschungseinrichtungen im Kontext von NFDI4Microbiota zur Verfügung gestellt.
Ziel des Projekts ist es, diese Datensätze strukturiert in Wikidata zu importieren.

Die Namen der Forschenden werden zunächst mit bestehenden Quellen wie ORCID, Scholia oder den Webseiten der beteiligten Projekte (z. B. 
NFDI4Microbiota, base4NFDI) abgeglichen.
Dabei wird geprüft, ob für die jeweilige Person bereits ein Wikidata-Eintrag existiert. 
Bereits vorhandene Einträge werden in diesem Projekt ignoriert; der Fokus liegt ausschließlich auf der Identifikation und Anlage neuer Einträge.

Für jede neue Person wird, sofern vorhanden, die ORCID iD aus dem ORCID-Verzeichnis recherchiert und dem Wikidata-Eintrag zugeordnet. 
Die ORCID iD wird als eigener Identifikator mit der entsprechenden Quelle in Wikidata hinterlegt.

Bereits existierende Objekte, die mit der betreffenden Person verknüpft werden können – wie z. B. 
Forschungseinrichtungen oder Projektbeteiligungen – werden als sogenannte “Unterobjekte” mit dem neuen Personeneintrag verbunden. 
Dabei wird zunächst mit Basisinformationen begonnen (Name, Institution, Identifikatoren) und der Eintrag bei ausreichender Projektlaufzeit um weitere Angaben ergänzt.
