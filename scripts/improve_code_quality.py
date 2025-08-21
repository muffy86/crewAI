#!/usr/bin/env python3
"""
Code Quality Improvement Script for CrewAI

This script automates the fixing of identified linting issues and provides
guidance for manual fixes that require human judgment.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple


class CodeQualityFixer:
    """Automates code quality improvements for CrewAI."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.src_path = self.project_root / "src" / "crewai"
        
    def run_ruff_check(self) -> Tuple[int, str]:
        """Run ruff check and return results."""
        cmd = ["ruff", "check", str(self.src_path), "--output-format=json"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode, result.stdout
        except FileNotFoundError:
            print("❌ Ruff not found. Please install with: pip install ruff")
            sys.exit(1)
    
    def auto_fix_issues(self) -> None:
        """Auto-fix issues that can be safely automated."""
        print("🔧 Running automatic fixes...")
        cmd = ["ruff", "check", str(self.src_path), "--fix", "--unsafe-fixes"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Auto-fixes completed successfully")
        else:
            print("⚠️  Some issues require manual attention")
            print(result.stdout)
    
    def identify_manual_fixes(self) -> List[Dict]:
        """Identify issues that need manual fixing."""
        manual_fixes = [
            {
                "file": "src/crewai/agents/agent_adapters/langgraph/structured_output_converter.py",
                "line": 77,
                "issue": "Bare except clause",
                "solution": "Replace 'except:' with specific exception types like 'except (ValueError, TypeError):'"
            },
            {
                "file": "src/crewai/agents/agent_adapters/langgraph/langgraph_adapter.py", 
                "line": 25,
                "issue": "Conditional import not handled properly",
                "solution": "Use try/except block or importlib.util.find_spec for optional imports"
            }
        ]
        return manual_fixes
    
    def create_pre_commit_hook(self) -> None:
        """Create a pre-commit hook to maintain code quality."""
        hook_content = """#!/bin/sh
# Pre-commit hook for CrewAI code quality

echo "🔍 Running code quality checks..."

# Run ruff
ruff check src/crewai/ --output-format=concise
if [ $? -ne 0 ]; then
    echo "❌ Linting issues found. Please fix before committing."
    exit 1
fi

# Run type checking
mypy src/crewai/ --ignore-missing-imports
if [ $? -ne 0 ]; then
    echo "❌ Type checking issues found. Please fix before committing."
    exit 1
fi

echo "✅ Code quality checks passed!"
"""
        
        hooks_dir = self.project_root / ".git" / "hooks"
        if hooks_dir.exists():
            hook_file = hooks_dir / "pre-commit"
            hook_file.write_text(hook_content)
            hook_file.chmod(0o755)
            print("✅ Pre-commit hook created successfully")
    
    def generate_fix_report(self) -> None:
        """Generate a detailed report of issues and fixes."""
        print("\n📊 Code Quality Improvement Report")
        print("=" * 50)
        
        # Run current check
        returncode, output = self.run_ruff_check()
        
        if returncode == 0:
            print("✅ No linting issues found!")
            return
        
        print(f"Found {len(output.splitlines())} issues")
        
        # Show manual fixes needed
        manual_fixes = self.identify_manual_fixes()
        if manual_fixes:
            print("\n🛠️  Manual Fixes Required:")
            for fix in manual_fixes:
                print(f"📁 {fix['file']}:{fix['line']}")
                print(f"   Issue: {fix['issue']}")
                print(f"   Solution: {fix['solution']}\n")
    
    def setup_development_environment(self) -> None:
        """Setup recommended development environment."""
        print("🔨 Setting up development environment...")
        
        # Create .vscode settings if not exists
        vscode_dir = self.project_root / ".vscode"
        vscode_dir.mkdir(exist_ok=True)
        
        settings = {
            "python.linting.enabled": True,
            "python.linting.ruffEnabled": True,
            "python.formatting.provider": "black",
            "python.formatting.blackArgs": ["--line-length", "88"],
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.organizeImports": True
            },
            "files.exclude": {
                "**/__pycache__": True,
                "**/*.pyc": True,
                ".pytest_cache": True,
                ".coverage": True,
                "htmlcov": True
            }
        }
        
        settings_file = vscode_dir / "settings.json"
        if not settings_file.exists():
            import json
            settings_file.write_text(json.dumps(settings, indent=2))
            print("✅ VS Code settings configured")
    
    def run_comprehensive_check(self) -> None:
        """Run all quality checks and improvements."""
        print("🚀 Starting comprehensive code quality improvement...")
        
        # Step 1: Auto-fix what we can
        self.auto_fix_issues()
        
        # Step 2: Generate report
        self.generate_fix_report()
        
        # Step 3: Setup development environment
        self.setup_development_environment()
        
        # Step 4: Create pre-commit hook
        self.create_pre_commit_hook()
        
        print("\n✨ Code quality improvement complete!")
        print("\n📝 Next Steps:")
        print("1. Review and manually fix remaining issues")
        print("2. Run tests to ensure nothing is broken")
        print("3. Commit changes in small, logical chunks")
        print("4. Set up your IDE with the provided settings")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = "."
    
    fixer = CodeQualityFixer(project_root)
    fixer.run_comprehensive_check()


if __name__ == "__main__":
    main()