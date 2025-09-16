#!/usr/bin/env python3
"""
Cosmere RPG PDF Processor
Extracts and structures content from PDF files for game use
"""

import os
from datetime import datetime
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import hashlib

# PDF processing libraries
try:
    import PyPDF2
    import pdfplumber
except ImportError:
    print("Please install required packages: pip install PyPDF2 pdfplumber")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ExtractedSection:
    """Represents an extracted section from the PDF"""
    title: str
    content: str
    page_number: int
    section_type: str  # 'rule', 'table', 'example', 'sidebar', etc.
    subsections: List['ExtractedSection'] = None
    metadata: Dict[str, Any] = None

class CosmereRPGPDFProcessor:
    """Main PDF processor for Cosmere RPG content"""
    
    def __init__(self, output_dir: str = "cosmere/data/rules"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.processed_files = []
        
        # Patterns for identifying different content types
        self.patterns = {
            'chapter': re.compile(r'^(Chapter|CHAPTER)\s+(\d+|[IVX]+)[:\s]+(.+)$', re.MULTILINE),
            'section': re.compile(r'^([A-Z][A-Za-z\s]+):?\s*$', re.MULTILINE),
            'subsection': re.compile(r'^([A-Z][a-z]+(?:\s+[A-Za-z]+)*)\s*$', re.MULTILINE),
            'stat_block': re.compile(r'(Strength|Speed|Intellect|Willpower|Awareness|Persuasion):\s*([+-]?\d+)'),
            'table_header': re.compile(r'^\|.*\|.*\|'),
            'rule_reference': re.compile(r'(?:see page|p\.|pg\.)\s*(\d+)', re.IGNORECASE),
            'dice_notation': re.compile(r'\b(\d+)?d\d+(?:[+-]\d+)?\b'),
            'investiture': re.compile(r'\b(Allomancy|Feruchemy|Hemalurgy|Surgebinding|AonDor|Awakening)\b', re.IGNORECASE)
        }
        
        # Cosmere-specific terms to track
        self.cosmere_terms = {
            'stats': ['Strength', 'Speed', 'Intellect', 'Willpower', 'Awareness', 'Persuasion'],
            'derived_stats': ['Deflect', 'Armor', 'Mental Fortitude', 'Physical Fortitude', 'HP'],
            'mechanics': ['Plot Die', 'Advantage', 'Disadvantage', 'Complication', 'Opportunity'],
            'investiture_types': ['Allomancy', 'Feruchemy', 'Hemalurgy', 'Surgebinding', 'AonDor', 
                                 'Awakening', 'Sand Mastery', 'Investiture Points'],
            'character_elements': ['Heritage', 'Path', 'Origin', 'Talents', 'Equipment']
        }
    
    def process_pdf(self, pdf_path: str, extract_images: bool = False) -> Dict[str, Any]:
        """
        Process a single PDF file and extract structured content
        
        Args:
            pdf_path: Path to the PDF file
            extract_images: Whether to extract images (requires more processing)
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        logger.info(f"Processing PDF: {pdf_path.name}")
        
        # Create output structure
        output = {
            'metadata': {
                'filename': pdf_path.name,
                'file_hash': self._calculate_file_hash(pdf_path),
                'pages': 0,
                'processing_date': datetime.fromtimestamp(os.path.getctime(str(pdf_path))).isoformat()
            },
            'content': {
                'chapters': [],
                'rules': [],
                'tables': [],
                'examples': [],
                'glossary': {},
                'index': {}
            },
            'search_index': []
        }
        
        try:
            # Use pdfplumber for better text extraction
            with pdfplumber.open(pdf_path) as pdf:
                output['metadata']['pages'] = len(pdf.pages)
                
                # Process each page
                for page_num, page in enumerate(pdf.pages, 1):
                    logger.info(f"Processing page {page_num}/{len(pdf.pages)}")
                    
                    # Extract text
                    text = page.extract_text()
                    if text:
                        # Process the page content
                        self._process_page_content(text, page_num, output)
                    
                    # Extract tables
                    tables = page.extract_tables()
                    for table in tables:
                        self._process_table(table, page_num, output)
                    
                    # Extract images if requested
                    if extract_images and hasattr(page, 'images'):
                        self._process_images(page.images, page_num, output)
            
            # Post-processing
            self._build_search_index(output)
            self._extract_glossary_terms(output)
            self._link_cross_references(output)
            
            # Save processed content
            self._save_output(output, pdf_path.stem)
            
            logger.info(f"Successfully processed {pdf_path.name}")
            return output
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            raise
    
    def _process_page_content(self, text: str, page_num: int, output: Dict) -> None:
        """Process text content from a page"""
        lines = text.split('\n')
        current_section = None
        content_buffer = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for chapter headers
            chapter_match = self.patterns['chapter'].match(line)
            if chapter_match:
                # Save previous section if exists
                if current_section and content_buffer:
                    self._save_section(current_section, '\n'.join(content_buffer), page_num, output)
                    content_buffer = []
                
                # Start new chapter
                current_section = {
                    'type': 'chapter',
                    'title': chapter_match.group(3),
                    'number': chapter_match.group(2)
                }
                continue
            
            # Check for section headers
            if self._is_section_header(line):
                # Save previous section
                if current_section and content_buffer:
                    self._save_section(current_section, '\n'.join(content_buffer), page_num, output)
                    content_buffer = []
                
                current_section = {
                    'type': 'section',
                    'title': line
                }
                continue
            
            # Check for game mechanics
            if self._contains_game_mechanics(line):
                self._extract_game_mechanics(line, page_num, output)
            
            # Add to content buffer
            content_buffer.append(line)
        
        # Save final section
        if current_section and content_buffer:
            self._save_section(current_section, '\n'.join(content_buffer), page_num, output)
    
    def _process_table(self, table: List[List[str]], page_num: int, output: Dict) -> None:
        """Process extracted table data"""
        if not table or len(table) < 2:
            return
        
        # Try to identify table type
        headers = table[0]
        table_type = self._identify_table_type(headers)
        
        table_data = {
            'headers': headers,
            'rows': table[1:],
            'page': page_num,
            'type': table_type
        }
        
        # Special processing for specific table types
        if table_type == 'talents':
            self._process_talent_table(table_data, output)
        elif table_type == 'equipment':
            self._process_equipment_table(table_data, output)
        elif table_type == 'powers':
            self._process_power_table(table_data, output)
        else:
            output['content']['tables'].append(table_data)
    
    def _extract_game_mechanics(self, text: str, page_num: int, output: Dict) -> None:
        """Extract specific game mechanics from text"""
        # Extract stat blocks
        stat_matches = self.patterns['stat_block'].findall(text)
        for stat, value in stat_matches:
            if 'stat_blocks' not in output['content']:
                output['content']['stat_blocks'] = []
            
            output['content']['stat_blocks'].append({
                'stat': stat,
                'value': int(value),
                'page': page_num,
                'context': text[:100]  # Include some context
            })
        
        # Extract dice notations
        dice_matches = self.patterns['dice_notation'].findall(text)
        for dice in dice_matches:
            if 'dice_references' not in output['content']:
                output['content']['dice_references'] = []
            
            output['content']['dice_references'].append({
                'notation': dice,
                'page': page_num,
                'context': text[:100]
            })
        
        # Extract Investiture references
        investiture_matches = self.patterns['investiture'].findall(text)
        for inv_type in investiture_matches:
            if 'investiture_references' not in output['content']:
                output['content']['investiture_references'] = {}
            
            if inv_type not in output['content']['investiture_references']:
                output['content']['investiture_references'][inv_type] = []
            
            output['content']['investiture_references'][inv_type].append({
                'page': page_num,
                'context': text[:200]
            })
    
    def _build_search_index(self, output: Dict) -> None:
        """Build searchable index of content"""
        index = []
        
        # Index all text content
        for content_type, content_list in output['content'].items():
            if isinstance(content_list, list):
                for item in content_list:
                    if isinstance(item, dict) and 'content' in item:
                        # Create searchable entry
                        entry = {
                            'type': content_type,
                            'title': item.get('title', ''),
                            'content': item.get('content', ''),
                            'page': item.get('page', 0),
                            'keywords': self._extract_keywords(item.get('content', ''))
                        }
                        index.append(entry)
        
        output['search_index'] = index
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        keywords = []
        
        # Check for Cosmere terms
        for category, terms in self.cosmere_terms.items():
            for term in terms:
                if term.lower() in text.lower():
                    keywords.append(term)
        
        # Extract dice notations
        dice_keywords = self.patterns['dice_notation'].findall(text)
        keywords.extend(dice_keywords)
        
        return list(set(keywords))
    
    def _save_output(self, output: Dict, filename_stem: str) -> None:
        """Save processed output to JSON files"""
        # Save main content
        main_output_path = self.output_dir / f"{filename_stem}_content.json"
        with open(main_output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        # Save search index separately for faster loading
        index_path = self.output_dir / f"{filename_stem}_index.json"
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(output['search_index'], f, indent=2, ensure_ascii=False)
        
        # Save quick reference
        quick_ref = self._create_quick_reference(output)
        quick_ref_path = self.output_dir / f"{filename_stem}_quick_ref.json"
        with open(quick_ref_path, 'w', encoding='utf-8') as f:
            json.dump(quick_ref, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved output to {self.output_dir}")
    
    def _create_quick_reference(self, output: Dict) -> Dict:
        """Create a quick reference summary"""
        return {
            'stats': self._extract_stat_references(output),
            'mechanics': self._extract_mechanic_references(output),
            'investiture': output['content'].get('investiture_references', {}),
            'tables': [{'title': t.get('type', 'Unknown'), 'page': t.get('page', 0)} 
                      for t in output['content'].get('tables', [])]
        }
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _is_section_header(self, line: str) -> bool:
        """Determine if a line is likely a section header"""
        # Simple heuristics for section headers
        if len(line) < 3 or len(line) > 50:
            return False
        
        # Check if line is mostly uppercase
        if line.isupper():
            return True
        
        # Check if line matches section pattern
        if self.patterns['section'].match(line):
            return True
        
        # Check for common section indicators
        section_indicators = ['Introduction', 'Overview', 'Rules', 'Example', 'Note:', 'Important:']
        return any(line.startswith(indicator) for indicator in section_indicators)
    
    def _contains_game_mechanics(self, line: str) -> bool:
        """Check if line contains game mechanics"""
        # Check for any Cosmere terms
        for category, terms in self.cosmere_terms.items():
            if any(term.lower() in line.lower() for term in terms):
                return True
        
        # Check for dice notation
        if self.patterns['dice_notation'].search(line):
            return True
        
        return False
    
    def _identify_table_type(self, headers: List[str]) -> str:
        """Identify the type of table based on headers"""
        headers_lower = [h.lower() for h in headers if h]
        
        # Check for talent table
        if any('talent' in h for h in headers_lower):
            return 'talents'
        
        # Check for equipment table
        if any(term in h for h in headers_lower for term in ['equipment', 'item', 'cost', 'weight']):
            return 'equipment'
        
        # Check for power table
        if any(term in h for h in headers_lower for term in ['power', 'investiture', 'metal', 'surge']):
            return 'powers'
        
        # Check for stat table
        if any(term in h for h in headers_lower for term in ['stat', 'modifier', 'bonus']):
            return 'stats'
        
        return 'general'
    
    def _save_section(self, section_info: Dict, content: str, page_num: int, output: Dict) -> None:
        """Save a content section to the appropriate output location"""
        section_data = {
            'title': section_info.get('title', ''),
            'content': content,
            'page': page_num,
            'type': section_info.get('type', 'general')
        }
        
        if section_info['type'] == 'chapter':
            section_data['number'] = section_info.get('number', '')
            output['content']['chapters'].append(section_data)
        else:
            # Categorize by content
            if self._is_rule_content(content):
                output['content']['rules'].append(section_data)
            elif 'example' in section_info.get('title', '').lower():
                output['content']['examples'].append(section_data)
            else:
                # Add to general rules
                output['content']['rules'].append(section_data)
    
    def _is_rule_content(self, content: str) -> bool:
        """Determine if content is a rule"""
        rule_indicators = ['must', 'cannot', 'should', 'may', 'roll', 'check', 'test']
        return any(indicator in content.lower() for indicator in rule_indicators)
    
    def _process_talent_table(self, table_data: Dict, output: Dict) -> None:
        """Process talent-specific tables"""
        if 'talents' not in output['content']:
            output['content']['talents'] = []
        
        for row in table_data['rows']:
            if len(row) >= 2:  # Assuming at least name and description
                talent = {
                    'name': row[0],
                    'description': row[1] if len(row) > 1 else '',
                    'tier': row[2] if len(row) > 2 else '',
                    'page': table_data['page']
                }
                output['content']['talents'].append(talent)
    
    def _process_equipment_table(self, table_data: Dict, output: Dict) -> None:
        """Process equipment-specific tables"""
        if 'equipment' not in output['content']:
            output['content']['equipment'] = []
        
        for row in table_data['rows']:
            if len(row) >= 2:
                item = {
                    'name': row[0],
                    'cost': row[1] if len(row) > 1 else '',
                    'weight': row[2] if len(row) > 2 else '',
                    'properties': row[3] if len(row) > 3 else '',
                    'page': table_data['page']
                }
                output['content']['equipment'].append(item)
    
    def _process_power_table(self, table_data: Dict, output: Dict) -> None:
        """Process Investiture power tables"""
        if 'powers' not in output['content']:
            output['content']['powers'] = []
        
        for row in table_data['rows']:
            if len(row) >= 2:
                power = {
                    'name': row[0],
                    'description': row[1],
                    'cost': row[2] if len(row) > 2 else '',
                    'page': table_data['page']
                }
                output['content']['powers'].append(power)
    
    def _extract_glossary_terms(self, output: Dict) -> None:
        """Extract glossary terms from content"""
        glossary = {}
        
        # Look for glossary section
        for chapter in output['content'].get('chapters', []):
            if 'glossary' in chapter.get('title', '').lower():
                # Parse glossary content
                lines = chapter['content'].split('\n')
                current_term = None
                definition = []
                
                for line in lines:
                    if line and line[0].isupper() and ':' in line:
                        # Save previous term
                        if current_term and definition:
                            glossary[current_term] = ' '.join(definition)
                        
                        # Start new term
                        parts = line.split(':', 1)
                        current_term = parts[0].strip()
                        definition = [parts[1].strip()] if len(parts) > 1 else []
                    elif current_term:
                        definition.append(line.strip())
                
                # Save last term
                if current_term and definition:
                    glossary[current_term] = ' '.join(definition)
        
        output['content']['glossary'] = glossary
    
    def _link_cross_references(self, output: Dict) -> None:
        """Link cross-references between sections"""
        # Find all page references
        for content_type, content_list in output['content'].items():
            if isinstance(content_list, list):
                for item in content_list:
                    if isinstance(item, dict) and 'content' in item:
                        # Find page references
                        refs = self.patterns['rule_reference'].findall(item.get('content', ''))
                        if refs:
                            item['references'] = [int(ref) for ref in refs]
    
    def _extract_stat_references(self, output: Dict) -> Dict:
        """Extract all stat references"""
        stats = {}
        
        for stat_block in output['content'].get('stat_blocks', []):
            stat_name = stat_block['stat']
            if stat_name not in stats:
                stats[stat_name] = []
            
            stats[stat_name].append({
                'value': stat_block['value'],
                'page': stat_block['page'],
                'context': stat_block['context']
            })
        
        return stats
    
    def _extract_mechanic_references(self, output: Dict) -> Dict:
        """Extract all mechanic references"""
        mechanics = {}
        
        # Extract from dice references
        for dice_ref in output['content'].get('dice_references', []):
            if 'dice_mechanics' not in mechanics:
                mechanics['dice_mechanics'] = []
            
            mechanics['dice_mechanics'].append({
                'notation': dice_ref['notation'],
                'page': dice_ref['page']
            })
        
        return mechanics
    
    def _process_images(self, images: List, page_num: int, output: Dict) -> None:
        """Process images from PDF (placeholder for future implementation)"""
        # This would extract and save images if needed
        # For now, just track image locations
        if 'images' not in output['content']:
            output['content']['images'] = []
        
        for img in images:
            output['content']['images'].append({
                'page': page_num,
                'bbox': img.get('bbox', []),
                'type': 'embedded_image'
            })


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process Cosmere RPG PDFs')
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--output-dir', default='cosmere/data/rules', help='Output directory')
    parser.add_argument('--extract-images', action='store_true', help='Extract images from PDF')
    
    args = parser.parse_args()
    
    processor = CosmereRPGPDFProcessor(output_dir=args.output_dir)
    
    try:
        result = processor.process_pdf(args.pdf_path, extract_images=args.extract_images)
        print(f"Successfully processed {args.pdf_path}")
        print(f"Extracted {len(result['content']['chapters'])} chapters")
        print(f"Found {len(result['content']['rules'])} rule sections")
        print(f"Found {len(result['content']['tables'])} tables")
        print(f"Created {len(result['search_index'])} searchable entries")
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())