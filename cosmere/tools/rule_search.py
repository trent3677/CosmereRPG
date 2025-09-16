"""
Cosmere RPG Rule Search and Lookup System
Provides fast searching through extracted PDF content
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import re
from difflib import get_close_matches

class CosmereRuleSearch:
    """Search engine for Cosmere RPG rules"""
    
    def __init__(self, rules_dir: str = "cosmere/data/rules"):
        self.rules_dir = Path(rules_dir)
        self.master_index = None
        self.search_index = []
        self.glossary = {}
        self.quick_ref = {}
        
        # Load indexes
        self._load_indexes()
    
    def _load_indexes(self):
        """Load all search indexes"""
        # Load master index
        master_path = self.rules_dir / 'master_index.json'
        if master_path.exists():
            with open(master_path, 'r', encoding='utf-8') as f:
                self.master_index = json.load(f)
                self.glossary = self.master_index.get('glossary', {})
                self.quick_ref = self.master_index.get('quick_reference', {})
        
        # Load individual search indexes
        for index_file in self.rules_dir.glob('*_index.json'):
            with open(index_file, 'r', encoding='utf-8') as f:
                self.search_index.extend(json.load(f))
    
    def search(self, query: str, limit: int = 10, search_type: str = 'all') -> List[Dict]:
        """
        Search for rules matching the query
        
        Args:
            query: Search term or phrase
            limit: Maximum number of results
            search_type: Type of search ('all', 'rules', 'tables', 'glossary', 'exact')
        
        Returns:
            List of matching results
        """
        query_lower = query.lower()
        results = []
        
        if search_type in ['all', 'glossary']:
            # Search glossary first for exact terms
            glossary_results = self._search_glossary(query)
            results.extend(glossary_results)
        
        if search_type in ['all', 'rules']:
            # Search rules
            rule_results = self._search_rules(query_lower)
            results.extend(rule_results)
        
        if search_type in ['all', 'tables']:
            # Search tables
            table_results = self._search_tables(query_lower)
            results.extend(table_results)
        
        # Sort by relevance score
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return results[:limit]
    
    def _search_glossary(self, query: str) -> List[Dict]:
        """Search glossary for exact or close matches"""
        results = []
        
        # Exact match
        if query in self.glossary:
            results.append({
                'type': 'glossary',
                'term': query,
                'definition': self.glossary[query],
                'score': 100,
                'exact_match': True
            })
        
        # Close matches
        close_matches = get_close_matches(query, self.glossary.keys(), n=3, cutoff=0.6)
        for match in close_matches:
            if match != query:  # Skip if already added as exact match
                results.append({
                    'type': 'glossary',
                    'term': match,
                    'definition': self.glossary[match],
                    'score': 80,
                    'exact_match': False
                })
        
        return results
    
    def _search_rules(self, query_lower: str) -> List[Dict]:
        """Search through rule content"""
        results = []
        
        if not self.master_index:
            return results
        
        for rule in self.master_index.get('rules', []):
            score = 0
            content_lower = rule.get('content', '').lower()
            title_lower = rule.get('title', '').lower()
            
            # Title match (higher score)
            if query_lower in title_lower:
                score += 50
                if title_lower.startswith(query_lower):
                    score += 20
            
            # Content match
            if query_lower in content_lower:
                # Count occurrences
                occurrences = content_lower.count(query_lower)
                score += min(30, occurrences * 10)
                
                # Extract context
                context = self._extract_context(content_lower, query_lower)
                
                results.append({
                    'type': 'rule',
                    'title': rule.get('title', 'Untitled'),
                    'content': context,
                    'page': rule.get('page', 0),
                    'source': rule.get('source', 'Unknown'),
                    'score': score,
                    'full_content': rule.get('content', '')
                })
        
        return results
    
    def _search_tables(self, query_lower: str) -> List[Dict]:
        """Search through tables"""
        results = []
        
        if not self.master_index:
            return results
        
        for table in self.master_index.get('tables', []):
            score = 0
            
            # Check headers
            headers_str = ' '.join(table.get('headers', [])).lower()
            if query_lower in headers_str:
                score += 40
            
            # Check rows
            rows_matched = 0
            for row in table.get('rows', []):
                row_str = ' '.join(str(cell) for cell in row).lower()
                if query_lower in row_str:
                    rows_matched += 1
            
            if rows_matched > 0:
                score += min(30, rows_matched * 10)
                
                results.append({
                    'type': 'table',
                    'table_type': table.get('type', 'general'),
                    'headers': table.get('headers', []),
                    'rows_matched': rows_matched,
                    'total_rows': len(table.get('rows', [])),
                    'page': table.get('page', 0),
                    'source': table.get('source', 'Unknown'),
                    'score': score
                })
        
        return results
    
    def _extract_context(self, content: str, query: str, context_size: int = 150) -> str:
        """Extract context around the search query"""
        index = content.find(query)
        if index == -1:
            return content[:context_size] + "..."
        
        start = max(0, index - context_size // 2)
        end = min(len(content), index + len(query) + context_size // 2)
        
        context = content[start:end]
        
        # Clean up context
        if start > 0:
            context = "..." + context
        if end < len(content):
            context = context + "..."
        
        return context
    
    def get_quick_reference(self, category: str) -> Dict:
        """Get quick reference for a category"""
        return self.quick_ref.get(category, {})
    
    def get_talent_by_name(self, talent_name: str) -> Optional[Dict]:
        """Find a specific talent by name"""
        talents = self.quick_ref.get('talents', [])
        
        for talent in talents:
            if talent.get('name', '').lower() == talent_name.lower():
                return talent
        
        # Try fuzzy match
        talent_names = [t.get('name', '') for t in talents]
        matches = get_close_matches(talent_name, talent_names, n=1, cutoff=0.6)
        
        if matches:
            for talent in talents:
                if talent.get('name', '') == matches[0]:
                    return talent
        
        return None
    
    def get_equipment_by_name(self, item_name: str) -> Optional[Dict]:
        """Find equipment by name"""
        equipment = self.quick_ref.get('equipment', [])
        
        for item in equipment:
            if item.get('name', '').lower() == item_name.lower():
                return item
        
        return None
    
    def search_by_page(self, page_number: int, source_filename: Optional[str] = None) -> List[Dict]:
        """Find all content from a specific page"""
        results = []
        
        # Search rules
        for rule in self.master_index.get('rules', []):
            if rule.get('page') == page_number:
                if not source_filename or rule.get('source') == source_filename:
                    results.append({
                        'type': 'rule',
                        'content': rule
                    })
        
        # Search tables
        for table in self.master_index.get('tables', []):
            if table.get('page') == page_number:
                if not source_filename or table.get('source') == source_filename:
                    results.append({
                        'type': 'table',
                        'content': table
                    })
        
        return results
    
    def get_stats_info(self) -> Dict[str, List]:
        """Get information about all stats"""
        return self.quick_ref.get('stats', {})
    
    def get_mechanics_info(self) -> Dict[str, List]:
        """Get information about game mechanics"""
        return self.quick_ref.get('mechanics', {})
    
    def format_search_result(self, result: Dict) -> str:
        """Format a search result for display"""
        result_type = result.get('type', 'unknown')
        
        if result_type == 'glossary':
            return f"**{result['term']}**: {result['definition']}"
        
        elif result_type == 'rule':
            return (f"**{result['title']}** (Page {result['page']}, {result['source']})\n"
                   f"{result['content']}")
        
        elif result_type == 'table':
            return (f"**Table: {result['table_type']}** (Page {result['page']}, {result['source']})\n"
                   f"Found in {result['rows_matched']} of {result['total_rows']} rows")
        
        return str(result)


def create_search_interface():
    """Create a command-line search interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Search Cosmere RPG rules')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--type', choices=['all', 'rules', 'tables', 'glossary'], 
                       default='all', help='Type of search')
    parser.add_argument('--limit', type=int, default=5, help='Maximum results')
    
    args = parser.parse_args()
    
    # Initialize search
    searcher = CosmereRuleSearch()
    
    # Perform search
    results = searcher.search(args.query, limit=args.limit, search_type=args.type)
    
    if not results:
        print(f"No results found for '{args.query}'")
        return
    
    print(f"\nFound {len(results)} result(s) for '{args.query}':\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {searcher.format_search_result(result)}")
        print("-" * 50)


if __name__ == '__main__':
    create_search_interface()