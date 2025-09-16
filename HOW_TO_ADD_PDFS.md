# How to Add Your Cosmere RPG PDFs

## Quick Start Guide

### Step 1: Set Up Directories
First, run the setup script to create the necessary folders:

```bash
python cosmere/tools/setup_pdfs.py
```

This will create a `cosmere/pdfs/` folder in your workspace.

### Step 2: Add Your PDFs
Since you're working locally, simply:

1. **Open your file manager** (Windows Explorer, Finder, etc.)
2. **Navigate to your workspace folder**: `/workspace/cosmere/pdfs/`
3. **Copy or move your Cosmere RPG PDFs** into this folder

Common PDFs to add:
- Cosmere RPG Core Rulebook
- Cosmere RPG Primer  
- Quick Start Guide
- Any adventure modules or supplements

### Step 3: Process the PDFs
Once your PDFs are in the folder, run:

```bash
python cosmere/tools/process_all_pdfs.py
```

This will:
- Extract all text content
- Parse rules, tables, and game mechanics
- Create searchable indexes
- Save everything to `cosmere/data/rules/`

### Step 4: Verify Processing
Check if it worked:

```bash
# List processed files
ls cosmere/data/rules/

# Search for a rule (example)
python cosmere/tools/rule_search.py "Plot Die"
```

## Alternative Methods

### If you're using WSL/Linux:
```bash
# Copy from Windows to WSL
cp /mnt/c/Users/YourName/Documents/CosmereRPG/*.pdf cosmere/pdfs/
```

### If you're using Docker:
```bash
# Copy into container
docker cp /path/to/your/pdfs/. container_name:/workspace/cosmere/pdfs/
```

### Using command line:
```bash
# Copy single file
cp ~/Downloads/cosmere-rpg-core.pdf cosmere/pdfs/

# Copy multiple files
cp ~/Downloads/*.pdf cosmere/pdfs/
```

## Important Notes

- PDFs are automatically gitignored for copyright protection
- PDFs stay local on your machine only
- The system extracts only the text/rules, not images
- Processing may take a few minutes for large PDFs

## Troubleshooting

### "No PDFs found"
- Check that files are in `cosmere/pdfs/` not subdirectories
- Ensure files have `.pdf` or `.PDF` extension

### "Permission denied"
- Make sure you have read permissions on the PDF files
- On Linux/Mac: `chmod 644 cosmere/pdfs/*.pdf`

### "Processing failed"
- Some PDFs may be password-protected or corrupted
- Try with a different PDF first to test
- Check the error message for details

## Next Steps

After processing your PDFs:

1. **Run the app**: `python run_cosmere.py`
2. **Access rules**: The app can now search and reference your PDFs
3. **Create characters**: Use the integrated rules for validation
4. **Play the game**: Enjoy Cosmere RPG with digital assistance!