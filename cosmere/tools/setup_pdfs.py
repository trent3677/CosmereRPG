#!/usr/bin/env python3
"""
Setup script for Cosmere RPG PDF processing
Creates necessary directories and provides instructions
"""

import os
import sys
from pathlib import Path

def setup_pdf_directories():
    """Create necessary directories for PDF processing"""
    
    # Define directory structure
    directories = [
        'cosmere/pdfs',           # Where you'll place your PDF files
        'cosmere/data/rules',     # Where processed rules will be stored
        'cosmere/data/search',    # Search index storage
        'cosmere/data/cache',     # Processing cache
    ]
    
    print("🌟 Cosmere RPG PDF Setup")
    print("=" * 50)
    
    # Create directories
    for dir_path in directories:
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {path}")
    
    # Create .gitignore for PDFs directory
    gitignore_path = Path('cosmere/pdfs/.gitignore')
    with open(gitignore_path, 'w') as f:
        f.write("# Ignore all PDFs (copyright protection)\n*.pdf\n*.PDF\n")
    print(f"✓ Created .gitignore in cosmere/pdfs/")
    
    # Create README for PDFs directory
    readme_path = Path('cosmere/pdfs/README.md')
    with open(readme_path, 'w') as f:
        f.write("""# Cosmere RPG PDFs Directory

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
""")
    print(f"✓ Created README in cosmere/pdfs/")
    
    print("\n" + "=" * 50)
    print("📚 Setup Complete!")
    print("\n📁 Now add your Cosmere RPG PDFs to:")
    print(f"   {os.path.abspath('cosmere/pdfs/')}")
    print("\n💡 Tips:")
    print("   - Simply copy/paste or drag your PDF files into that folder")
    print("   - The PDFs will stay on your local machine")
    print("   - Run process_all_pdfs.py after adding PDFs")
    
    # Check if any PDFs already exist
    pdf_path = Path('cosmere/pdfs')
    existing_pdfs = list(pdf_path.glob('*.pdf')) + list(pdf_path.glob('*.PDF'))
    
    if existing_pdfs:
        print(f"\n✨ Found {len(existing_pdfs)} existing PDF(s):")
        for pdf in existing_pdfs:
            print(f"   - {pdf.name}")
        print("\n🚀 Ready to process these PDFs!")
    else:
        print("\n⚠️  No PDFs found yet. Add your PDFs to the folder above.")
    
    return len(existing_pdfs)

if __name__ == '__main__':
    num_pdfs = setup_pdf_directories()
    
    # Return appropriate exit code
    sys.exit(0 if num_pdfs > 0 else 1)