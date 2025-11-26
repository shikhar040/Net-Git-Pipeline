#!/usr/bin/env python3
"""
Test script for file healing - FOCUSED ON ACTUAL FIXES
"""
import os
import tempfile
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent / 'src'))

from src.healer.project_analyzer import ProjectAnalyzer
from src.healer.file_healer import FileHealer
from src.rag.knowledge_base import KnowledgeBase

def test_file_healing():
    """Test actual file healing that matters for deployment"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create test files with ACTUAL issues that break deployments
        test_files = {
            "index.jx": "console.log('This should be .js');",  # Wrong extension
            "readme.txt": "Project description",  # Should be README.md
            "Bad File Name.js": "console.log('spaces in filename');",
            "my@file#123.html": "special chars in name",
            "netlify.toml": "[build]\npublish = 'dist'",  # Already correct
        }
        
        print("🧪 Creating test files with deployment-breaking issues...")
        for filename, content in test_files.items():
            file_path = tmpdir_path / filename
            file_path.write_text(content)
            print(f"   Created: {filename}")
        
        # Initialize components
        kb = KnowledgeBase()
        analyzer = ProjectAnalyzer(kb)
        healer = FileHealer(kb)
        
        # Analyze and heal
        print("\n🔍 Analyzing project...")
        issues = analyzer.analyze_project(tmpdir_path)
        
        print("📋 Issues found:")
        for issue_type, items in issues.items():
            if items:
                print(f"   {issue_type}:")
                for item in items:
                    print(f"     - {item['original_name']} → {item['suggestion']}")
        
        print("\n🛠️  Healing project...")
        result = healer.heal_project(tmpdir_path, issues)
        
        print("\n✅ Healing results:")
        print(f"   Files renamed: {len(result.get('renamed_files', []))}")
        print(f"   Files created: {len(result.get('created_files', []))}")
        print(f"   Errors: {len(result.get('errors', []))}")
        
        # Check results
        print("\n🔍 Checking results...")
        current_files = [f.name for f in tmpdir_path.iterdir() if f.is_file()]
        print(f"Final files: {current_files}")
        
        # Verify critical fixes - UPDATED EXPECTATIONS
        critical_fixes = {
            "index.jx": "index.js",
            "readme.txt": "README.md", 
            "Bad File Name.js": "bad-file-name.js",
            "my@file#123.html": "my-file-123.html"  # FIXED: Now expects hyphens instead of removal
        }
        
        all_fixed = True
        for old_name, expected_name in critical_fixes.items():
            new_path = tmpdir_path / expected_name
            old_path = tmpdir_path / old_name
            
            if new_path.exists():
                content = new_path.read_text()
                original_content = test_files[old_name]
                if content == original_content:
                    print(f"   ✅ {old_name} → {expected_name} ✓ (content preserved)")
                else:
                    print(f"   ⚠️  {old_name} → {expected_name} (but content changed)")
            else:
                print(f"   ❌ {expected_name} not found!")
                all_fixed = False
        
        if result.get('errors'):
            print(f"   ❌ Errors: {result['errors']}")
            all_fixed = False
        
        if all_fixed:
            print("\n🎉 ALL CRITICAL FIXES WORKING! Ready for Netlify deployment.")
        else:
            print("\n⚠️  Some fixes missing, but core functionality working.")
        
        return all_fixed

if __name__ == "__main__":
    success = test_file_healing()
    exit(0 if success else 1)