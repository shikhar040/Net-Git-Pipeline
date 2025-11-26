import json
import re
from pathlib import Path
from typing import Dict, Any

class KnowledgeBase:
    def __init__(self):
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict[str, Any]:
        """Load healing rules from config"""
        return {
            "file_naming": {
                "recommended": "kebab-case",
                "allowed_chars": "a-z0-9.-",
                "max_length": 50,
            },
            "required_files": {
                "netlify": ["netlify.toml"],
                "web": ["index.html", "package.json"]
            },
            "file_corrections": {
                "index.jx": "index.js",
                "index.htm": "index.html",
                "readme.txt": "README.md",
                "package-lock.json": "package-lock.json",
                "node_modules": "node_modules"
            }
        }
    
    def generate_suggestion(self, original_name: str) -> str:
        """Generate suggested name - FIXED SPECIAL CHARACTER HANDLING"""
        # Check for known file corrections first
        file_corrections = self.rules.get("file_corrections", {})
        if original_name in file_corrections:
            return file_corrections[original_name]
        
        # Fix common file extensions
        extension_fixes = {
            '.jx': '.js',
            '.htm': '.html',
            '.txt': '.md',
            '.jsx': '.js'
        }
        
        path = Path(original_name)
        stem = path.stem
        suffix = path.suffix.lower()
        
        # Fix file extensions
        if suffix in extension_fixes:
            suffix = extension_fixes[suffix]
        
        # Convert filename to kebab-case - FIXED VERSION
        suggestion = stem
        
        # Step 1: Replace spaces and underscores with hyphens
        suggestion = re.sub(r'[\s_]+', '-', suggestion)
        
        # Step 2: Replace special characters with hyphens (not remove them)
        suggestion = re.sub(r'[^a-zA-Z0-9.-]+', '-', suggestion)
        
        # Step 3: Convert to lowercase
        suggestion = suggestion.lower()
        
        # Step 4: Clean up multiple hyphens
        suggestion = re.sub(r'-+', '-', suggestion)
        suggestion = suggestion.strip('-')
        
        if not suggestion:
            suggestion = 'file'
        
        # Add extension back
        if suffix:
            suggestion += suffix
        
        return suggestion
    
    def get_file_template(self, filename: str) -> str:
        """Get template content for missing files"""
        templates = {
            'netlify.toml': '''[build]
  command = "npm run build"
  publish = "dist"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
''',
            'package.json': '''{
  "name": "auto-healed-project",
  "version": "1.0.0",
  "scripts": {
    "build": "echo 'Build completed'",
    "dev": "echo 'Development server'"
  }
}
''',
            'index.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auto-Healed Project</title>
</head>
<body>
    <h1>Hello from Auto-Healing Pipeline!</h1>
</body>
</html>''',
            'index.js': '// Auto-generated entry point\nconsole.log("App started!");',
            'README.md': '# Auto-Healed Project\n\nThis project was automatically healed by the pipeline.'
        }
        return templates.get(filename, f'# Auto-generated {filename}\n')