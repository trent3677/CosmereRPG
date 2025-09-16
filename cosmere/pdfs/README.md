# Cosmere RPG PDFs Directory

## How to Add Your PDFs

1. **Copy your Cosmere RPG PDF files to this directory**
   - Place files directly in `cosmere/pdfs/`
   - Supported formats: .pdf, .PDF

2. **Recommended PDFs to add:**
   - Cosmere RPG Core Rulebook
   - Cosmere RPG Primer
   - Quick Start Guide
   - Any supplemental materials

3. **Important Notes:**
   - PDFs are gitignored for copyright protection
   - PDFs stay local on your machine only
   - Processed rules are stored in `cosmere/data/rules/`

## Processing Your PDFs

After adding PDFs, run:
```bash
python cosmere/tools/process_all_pdfs.py
```

This will extract and structure all game content for use in the app.
