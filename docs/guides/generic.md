# Guide: Generic Document Collection

Use local-rag with any folder of documents — PDFs, Word files, Markdown, Excel, or BibTeX.

## Supported Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| Markdown | `.md` | Full text extraction |
| PDF | `.pdf` | Digital PDFs only (not scanned) |
| Word | `.docx` | Text and tables |
| Excel | `.xlsx` | Cell content as text |
| BibTeX | `.bib` | Academic references |

## Configuration

Add one entry per document source in `config.yaml`:

```yaml
sources:
  my_reports:
    path: "/path/to/reports"
    include_all: true
    extensions: [".pdf", ".docx"]

  my_notes:
    path: "/path/to/notes"
    include_all: true
    extensions: [".md"]

  my_references:
    path: "/path/to/references"
    include_all: false
    extensions: [".bib"]
```

## Ingestion

```bash
conda activate local-rag
python ingest.py
```

## Watching for Changes

```bash
python watcher.py   # polls every 60 seconds by default
```

## Querying

```
query_rag("What are the main findings in Q3 reports?")
query_rag("Summarize the regulatory requirements across all documents", mode="global")
```
