#!/usr/bin/env python3
"""
Simple Auto-Healer - All in one file
"""
import os
import re
import shutil
import json
from pathlib import Path
from typing import Dict, List, Any

class SimpleKnowledgeBase:
    def __init__(self):
        self.rules = {
            "file_corrections": {
                "index.jx": "index.js",
                "index.htm": "index.html", 
                "readme.txt": "README.md",
            },
            "extension_fixes": {
                '.jx': '.js',
                '.htm': '.html',
                '.txt': '.md',
            }
        }
    
    def generate_suggestion(self, original_name: str) -> str:
        """Generate suggested name"""
        # Check for known corrections
        if original_name in self.rules["file_corrections"]:
            return self.rules["file_corrections"][original_name]
        
        path = Path(original_name)
        stem = path.stem
        suffix = path.suffix.lower()
        
        # Fix extensions
        if suffix in self.rules["extension_fixes"]:
            suffix = self.rules["extension_fixes"][suffix]
        
        # Convert to kebab-case
        suggestion = stem
        suggestion = re.sub(r'[\s_]+', '-', suggestion)
        suggestion = re.sub(r'[^a-zA-Z0-9.-]+', '-', suggestion)
        suggestion = suggestion.lower()
        suggestion = re.sub(r'-+', '-', suggestion)
        suggestion = suggestion.strip('-')
        
        if not suggestion:
            suggestion = 'file'
        
        if suffix:
            suggestion += suffix
        
        return suggestion

class SimpleHealer:
    def __init__(self):
        self.kb = SimpleKnowledgeBase()
    
    def analyze_project(self, project_path: Path) -> Dict[str, List]:
        """Analyze project for issues"""
        issues = {'invalid_filenames': []}
        
        for root, dirs, files in os.walk(project_path):
            # Skip certain directories
            if 'node_modules' in root or '.git' in root:
                continue
                
            for file in files:
                file_path = Path(root) / file
                suggestion = self.kb.generate_suggestion(file)
                
                if suggestion != file:
                    issues['invalid_filenames'].append({
                        'path': str(file_path),
                        'original_name': file,
                        'suggestion': suggestion
                    })
        
        return issues
    
    def heal_project(self, project_path: Path, issues: Dict[str, List]) -> Dict[str, Any]:
        """Apply fixes"""
        healing_report = {'renamed_files': [], 'errors': []}
        
        for issue in issues.get('invalid_filenames', []):
            try:
                old_path = Path(issue['path'])
                new_path = old_path.parent / issue['suggestion']
                
                if old_path.exists() and old_path != new_path:
                    shutil.copy2(old_path, new_path)
                    old_path.unlink()
                    healing_report['renamed_files'].append({
                        'from': str(old_path),
                        'to': str(new_path)
                    })
                    print(f"✅ Fixed: {old_path.name} → {new_path.name}")
                    
            except Exception as e:
                healing_report['errors'].append(f"Error fixing {issue['path']}: {str(e)}")
        
        return healing_report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple Auto-Healer')
    parser.add_argument('--path', default='.', help='Project path')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed')
    
    args = parser.parse_args()
    
    healer = SimpleHealer()
    project_path = Path(args.path)
    
    print("🔍 Analyzing project...")
    issues = healer.analyze_project(project_path)
    
    if not issues['invalid_filenames']:
        print("✅ No issues found!")
        return
    
    print(f"\n📋 Found {len(issues['invalid_filenames'])} issues:")
    for issue in issues['invalid_filenames']:
        print(f"   - {issue['original_name']} → {issue['suggestion']}")
    
    if args.dry_run:
        print("\n💡 Dry run completed. Run without --dry-run to fix these issues.")
        return
    
    print("\n🛠️  Fixing issues...")
    result = healer.heal_project(project_path, issues)
    
    print(f"\n✅ Fixed {len(result['renamed_files'])} files!")
    if result['errors']:
        print(f"❌ Errors: {result['errors']}")

if __name__ == "__main__":
    main()