#!/usr/bin/env python3
"""
Simple script to check project structure
"""
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def check_project():
    print("🔍 Checking your project structure...")
    
    # Check current files
    current_files = [f for f in os.listdir('.') if os.path.isfile(f)]
    print(f"\n📁 Current files: {current_files}")
    
    # Check for problematic files
    problematic_extensions = ['.jx', '.htm', ' ']  # files with spaces or wrong extensions
    problematic_files = []
    
    for file in current_files:
        if any(problem in file for problem in problematic_extensions):
            problematic_files.append(file)
    
    if problematic_files:
        print(f"\n❌ Problematic files found:")
        for file in problematic_files:
            print(f"   - {file}")
        print(f"\n💡 Run the auto-healer to fix these files!")
    else:
        print(f"\n✅ No obviously problematic files found!")
    
    # Check if src structure exists
    print(f"\n📁 Checking src structure...")
    if os.path.exists('src'):
        src_contents = []
        for root, dirs, files in os.walk('src'):
            for file in files:
                if file.endswith('.py'):
                    src_contents.append(os.path.join(root, file))
        
        if src_contents:
            print("✅ src structure found with files:")
            for file in src_contents[:10]:  # Show first 10 files
                print(f"   - {file}")
        else:
            print("❌ src directory exists but no Python files found")
    else:
        print("❌ src directory not found")

if __name__ == "__main__":
    check_project()