# Guide: Zotero + local-rag

Query your Zotero PDF library and BibTeX references from Claude Code.

## Prerequisites

- Zotero installed with your library synced locally
- [local-rag installed](../../README.md#quickstart)

## Find Your Zotero Storage Path

In Zotero: Edit → Preferences → Advanced → Files and Folders → Data Directory Location.

Your PDFs are in `<Data Directory>/storage/`.

## Configuration

```yaml
sources:
  zotero:
    path: "/path/to/zotero/storage"   # the storage/ subfolder
    include_all: true
    extensions: [".pdf"]
```

## Initial Ingestion

```bash
conda activate local-rag
python ingest.py
```

PDFs are extracted with PyMuPDF. Scanned PDFs (image-only) are skipped — only
digitally-created PDFs are indexed.

## Querying Academic Papers

```
query_rag("What does the literature say about self-organization in VSM?")
query_rag("Find papers about quantum cognition and decision making", mode="global")
query_rag("Which authors discuss viable system model and complexity?", mode="hybrid")
```

## Tips

- BibTeX files (`.bib`) from Zotero exports are also supported — add them as a separate source
- For large libraries (500+ PDFs), first ingestion may take several hours
- The checkpoint system ensures you only process new papers on subsequent runs
