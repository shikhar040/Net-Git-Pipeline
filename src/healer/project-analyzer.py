import os
import re
from pathlib import Path
from typing import Dict, List
from ..utils.logger import setup_logger

logger = setup_logger()

class ProjectAnalyzer:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
    
    def analyze_project(self, project_path: Path) -> Dict[str, List]:
        """Analyze project structure and identify issues - SIMPLIFIED"""
        issues = {
            'invalid_filenames': [],
            'missing_files': [],
        }
        
        # Analyze all files
        for root, dirs, files in os.walk(project_path):
            # Skip node_modules and git directories
            if 'node_modules' in root or '.git' in root:
                continue
                
            for file in files:
                file_path = Path(root) / file
                self._analyze_file(file_path, issues, project_path)
        
        return {k: v for k, v in issues.items() if v}
    
    def _analyze_file(self, file_path: Path, issues: Dict, project_path: Path):
        """Analyze individual file"""
        filename = file_path.name
        
        # Skip certain files
        if filename in ['package-lock.json', 'yarn.lock']:
            return
        
        # Get suggested name
        suggestion = self.kb.generate_suggestion(filename)
        
        # If suggestion is different, add to issues
        if suggestion != filename:
            issues['invalid_filenames'].append({
                'path': str(file_path),
                'original_name': filename,
                'suggestion': suggestion,
                'reason': f'Should be {suggestion}'
            })
        
        # Check for required Netlify files in root
        if file_path.parent == project_path:
            required_files = self.kb.rules.get('required_files', {}).get('netlify', [])
            for req_file in required_files:
                req_path = project_path / req_file
                if not req_path.exists() and req_file not in [i['suggestion'] for i in issues.get('missing_files', [])]:
                    issues['missing_files'].append({
                        'file': req_file,
                        'reason': f'Required for Netlify deployment'
                    })