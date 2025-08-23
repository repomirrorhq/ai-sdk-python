#!/usr/bin/env python3
"""Basic structure validation test - no dependencies required."""

import ast
import os
import sys
from pathlib import Path


def validate_python_file(filepath):
    """Validate a Python file for syntax and basic structure."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST to check for syntax errors
        ast.parse(content)
        
        # Check for basic Python patterns
        issues = []
        
        # Check for potential async/await issues
        if 'yield from' in content and 'async def' in content:
            issues.append("Potential yield from in async function")
        
        # Check for await outside async function
        lines = content.split('\n')
        in_async_function = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('async def'):
                in_async_function = True
            elif stripped.startswith('def ') and not stripped.startswith('def async'):
                in_async_function = False
            elif 'await ' in stripped and not in_async_function:
                # Check if it's in a comment or string
                if not (stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''")):
                    issues.append(f"Line {i+1}: await outside async function")
        
        return True, issues
        
    except SyntaxError as e:
        return False, [f"Syntax error: {e}"]
    except Exception as e:
        return False, [f"Error: {e}"]


def validate_structure():
    """Validate the overall structure of the AI SDK Python package."""
    src_dir = Path("src/ai_sdk")
    
    if not src_dir.exists():
        print("❌ src/ai_sdk directory not found")
        return False
    
    # Check main modules exist
    required_modules = [
        "__init__.py",
        "core/__init__.py", 
        "providers/__init__.py",
        "tools/__init__.py",
        "errors/__init__.py",
    ]
    
    missing_modules = []
    for module in required_modules:
        if not (src_dir / module).exists():
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing required modules: {missing_modules}")
        return False
    
    print("✅ Core module structure is valid")
    
    # Count provider files
    providers_dir = src_dir / "providers"
    provider_files = list(providers_dir.glob("*/"))
    provider_count = len([d for d in provider_files if d.is_dir() and not d.name.startswith('_')])
    
    print(f"📦 Found {provider_count} provider directories")
    
    return True


def main():
    """Main validation function."""
    print("🔍 AI SDK Python - Basic Structure Validation")
    print("=" * 50)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Validate overall structure
    if not validate_structure():
        sys.exit(1)
    
    # Validate all Python files
    python_files = list(Path("src").glob("**/*.py"))
    print(f"\n🐍 Validating {len(python_files)} Python files...")
    
    total_issues = 0
    files_with_issues = 0
    
    for filepath in python_files:
        valid, issues = validate_python_file(filepath)
        
        if not valid:
            print(f"❌ {filepath}: SYNTAX ERROR")
            for issue in issues:
                print(f"   {issue}")
            files_with_issues += 1
            total_issues += len(issues)
        elif issues:
            print(f"⚠️  {filepath}: {len(issues)} warnings")
            for issue in issues:
                print(f"   {issue}")
            files_with_issues += 1
            total_issues += len(issues)
    
    # Summary
    print(f"\n📊 Validation Summary:")
    print(f"   Total files checked: {len(python_files)}")
    print(f"   Files with issues: {files_with_issues}")
    print(f"   Total issues: {total_issues}")
    
    if total_issues == 0:
        print("✅ All Python files are valid!")
        return True
    else:
        print(f"❌ Found {total_issues} issues in {files_with_issues} files")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)