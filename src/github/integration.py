import subprocess
import os
from pathlib import Path
from ..utils.logger import setup_logger

logger = setup_logger()

class GitHubIntegration:
    def __init__(self, github_token: str):
        self.github_token = github_token
    
    def commit_changes(self, repo_path: Path, commit_message: str) -> dict:
        """Commit and push changes to GitHub"""
        try:
            # Check if there are changes
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if not result.stdout.strip():
                return {'status': 'no_changes'}
            
            # Add all changes
            subprocess.run(['git', 'add', '.'], cwd=repo_path, check=True)
            
            # Commit changes
            subprocess.run(
                ['git', 'commit', '-m', commit_message],
                cwd=repo_path,
                check=True
            )
            
            # Push changes
            push_result = subprocess.run(
                ['git', 'push'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if push_result.returncode == 0:
                logger.info("✅ Changes committed and pushed to GitHub")
                return {'status': 'success'}
            else:
                return {'status': 'push_failed', 'error': push_result.stderr}
                
        except subprocess.CalledProcessError as e:
            error_msg = f"Git operation failed: {str(e)}"
            logger.error(error_msg)
            return {'status': 'error', 'error': error_msg}