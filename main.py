#!/usr/bin/env python3
"""
Auto-Healing Pipeline Main Entry Point - FIXED IMPORTS
"""
import os
import sys
import argparse
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.healer.project_analyzer import ProjectAnalyzer
    from src.healer.file_healer import FileHealer
    from src.rag.knowledge_base import KnowledgeBase
    from src.github.integration import GitHubIntegration
    from src.utils.logger import setup_logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("📁 Checking if all required files exist...")
    
    # Check if required directories exist
    required_dirs = ['src/healer', 'src/rag', 'src/github', 'src/utils']
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            print(f"   Missing directory: {dir_path}")
    
    # Check if required files exist
    required_files = [
        'src/healer/project_analyzer.py',
        'src/healer/file_healer.py', 
        'src/rag/knowledge_base.py',
        'src/utils/logger.py'
    ]
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"   Missing file: {file_path}")
    
    sys.exit(1)

logger = setup_logger()

class AutoHealingPipeline:
    def __init__(self, repo_path: str, github_token: str = None):
        self.repo_path = Path(repo_path)
        self.github_token = github_token
        self.knowledge_base = KnowledgeBase()
        self.analyzer = ProjectAnalyzer(self.knowledge_base)
        self.healer = FileHealer(self.knowledge_base)
        self.github = GitHubIntegration(github_token) if github_token else None
    
    def run(self, auto_commit: bool = False, dry_run: bool = False) -> dict:
        """Run the complete auto-healing pipeline"""
        logger.info("🚀 Starting Auto-Healing Pipeline")
        
        if dry_run:
            logger.info("🔍 DRY RUN MODE - No changes will be made")
        
        # Step 1: Analyze project
        logger.info("🔍 Analyzing project structure...")
        issues = self.analyzer.analyze_project(self.repo_path)
        
        if not issues:
            logger.info("✅ No issues found!")
            return {"status": "healthy", "issues": []}
        
        print(f"\n📋 Found {sum(len(v) for v in issues.values())} issues:")
        for issue_type, items in issues.items():
            if items:
                print(f"   {issue_type}: {len(items)}")
                for item in items:
                    if 'original_name' in item:
                        print(f"     - {item['original_name']} → {item['suggestion']}")
                    else:
                        print(f"     - {item.get('file', 'Unknown')}")
        
        if dry_run:
            print("\n💡 This is a dry run. Run without --dry-run to actually fix these issues.")
            return {"status": "dry_run", "issues": issues}
        
        # Step 2: Apply healing
        logger.info("🛠️ Applying fixes...")
        healing_report = self.healer.heal_project(self.repo_path, issues)
        
        # Step 3: Commit changes if requested
        if auto_commit and self.github and healing_report.get('renamed_files'):
            logger.info("📝 Committing changes to GitHub...")
            commit_result = self.github.commit_changes(
                self.repo_path,
                "Auto-heal: Fix file naming and project structure issues"
            )
            healing_report['commit'] = commit_result
        
        logger.info("🎉 Auto-healing completed!")
        
        # Print summary
        print("\n" + "="*50)
        print("AUTO-HEALING SUMMARY")
        print("="*50)
        print(f"Files renamed: {len(healing_report.get('renamed_files', []))}")
        print(f"Files created: {len(healing_report.get('created_files', []))}")
        print(f"Errors: {len(healing_report.get('errors', []))}")
        
        return healing_report

def main():
    parser = argparse.ArgumentParser(description='Auto-Healing Pipeline')
    parser.add_argument('--path', default='.', help='Project path')
    parser.add_argument('--auto-commit', action='store_true', help='Auto commit changes')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed without making changes')
    parser.add_argument('--github-token', help='GitHub token')
    
    args = parser.parse_args()
    
    pipeline = AutoHealingPipeline(args.path, args.github_token)
    result = pipeline.run(auto_commit=args.auto_commit, dry_run=args.dry_run)
    
    if result.get('errors'):
        print(f"\n❌ Errors encountered: {result['errors']}")
        sys.exit(1)

if __name__ == "__main__":
    main()