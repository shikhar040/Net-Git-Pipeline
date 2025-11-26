import os
import shutil
from pathlib import Path
from typing import Dict, List, Any
from ..utils.logger import setup_logger

logger = setup_logger()

class FileHealer:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
    
    def heal_project(self, project_path: Path, issues: Dict[str, List]) -> Dict[str, Any]:
        """Apply fixes to the project - SIMPLIFIED"""
        healing_report = {
            'renamed_files': [],
            'created_files': [],
            'errors': []
        }
        
        # Fix invalid filenames
        for issue in issues.get('invalid_filenames', []):
            self._fix_file(Path(issue['path']), issue['suggestion'], healing_report)
        
        # Create missing files
        for issue in issues.get('missing_files', []):
            self._create_file(project_path, issue['file'], healing_report)
        
        return healing_report
    
    def _fix_file(self, old_path: Path, new_name: str, report: Dict):
        """Fix individual file"""
        try:
            new_path = old_path.parent / new_name
            
            # Skip if same file (case insensitive)
            if old_path.name.lower() == new_name.lower():
                return
            
            # Copy content to new file
            if old_path.exists():
                shutil.copy2(old_path, new_path)
                
                # Delete old file only if different from new file
                if old_path.resolve() != new_path.resolve():
                    old_path.unlink()
                
                report['renamed_files'].append({
                    'from': str(old_path),
                    'to': str(new_path)
                })
                logger.info(f"✅ Fixed: {old_path.name} → {new_name}")
                
        except Exception as e:
            error_msg = f"Error fixing {old_path}: {str(e)}"
            report['errors'].append(error_msg)
            logger.error(error_msg)
    
    def _create_file(self, project_path: Path, filename: str, report: Dict):
        """Create missing file"""
        try:
            file_path = project_path / filename
            
            if not file_path.exists():
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                template = self.kb.get_file_template(filename)
                file_path.write_text(template)
                
                report['created_files'].append(str(file_path))
                logger.info(f"✅ Created: {filename}")
                
        except Exception as e:
            error_msg = f"Error creating {filename}: {str(e)}"
            report['errors'].append(error_msg)
            logger.error(error_msg)