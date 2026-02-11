"""
Rename project from Multi-Agent HR Intelligence Platform to Multi-Agent HR Intelligence Platform
"""
import os
import re
from pathlib import Path

# Mapping of old names to new names
REPLACEMENTS = {
    "Multi-Agent HR Intelligence Platform": "Multi-Agent HR Intelligence Platform",
    "Multi-Agent HR Intelligence Platform": "Multi-Agent HR Intelligence Platform",
    "Multi-Agent HR Intelligence Platform": "Multi-Agent HR Intelligence Platform",
    "Multi-Agent HR Intelligence Platform": "Multi-Agent HR Intelligence Platform",
}

# File extensions to process
EXTENSIONS = ['.md', '.py', '.html', '.css', '.json', '.txt']

# Directories to skip
SKIP_DIRS = {'.git', '__pycache__', 'node_modules', '.pytest_cache', 'venv', 'env', '.venv'}

def should_process_file(file_path):
    """Check if file should be processed"""
    # Skip if in excluded directory
    for skip_dir in SKIP_DIRS:
        if skip_dir in file_path.parts:
            return False

    # Only process specific extensions
    return file_path.suffix in EXTENSIONS

def replace_in_file(file_path):
    """Replace text in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Apply all replacements
        for old_text, new_text in REPLACEMENTS.items():
            content = content.replace(old_text, new_text)

        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function"""
    project_root = Path(__file__).parent
    files_updated = 0

    print("Starting project rename...")
    print(f"Root directory: {project_root}")
    print()

    # Walk through all files
    for file_path in project_root.rglob('*'):
        if file_path.is_file() and should_process_file(file_path):
            if replace_in_file(file_path):
                print(f"[OK] Updated: {file_path.relative_to(project_root)}")
                files_updated += 1

    print()
    print(f"Completed! Updated {files_updated} files.")
    print()
    print("Replacements made:")
    for old, new in REPLACEMENTS.items():
        print(f"  '{old}' → '{new}'")

if __name__ == "__main__":
    main()
