#!/usr/bin/env python3
"""
Script to push all remaining files to GitHub repository.
"""
import os
import subprocess
import json
from pathlib import Path

REPO_OWNER = "sebastiannorton"
REPO_NAME = "isengard-delay-verb"
BRANCH = "main"
BASE_DIR = Path("/workspace/isengard-project")

# Files to exclude
EXCLUDE_PATTERNS = [
    ".git",
    ".rea-node_modules",
    "reference-plugins",
    "{research,tests",  # This is a malformed directory
    ".vibe",
    "__pycache__",
    ".pyc",
    ".zip",
    "zi*",
]

def should_exclude(path):
    """Check if a path should be excluded."""
    path_str = str(path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return True
    return False

def get_github_file_list():
    """Get list of files already in GitHub repo."""
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{REPO_OWNER}/{REPO_NAME}/git/trees/{BRANCH}?recursive=1"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {f['path'] for f in data.get('tree', []) if f['type'] == 'blob'}
    except Exception as e:
        print(f"Error getting GitHub file list: {e}")
    return set()

def get_local_file_list():
    """Get list of all local files to push."""
    files = []
    for root, dirs, filenames in os.walk(BASE_DIR):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]
        
        for filename in filenames:
            filepath = Path(root) / filename
            if not should_exclude(filepath) and not filename.endswith('.pyc'):
                # Get relative path
                rel_path = filepath.relative_to(BASE_DIR)
                files.append(str(rel_path))
    return set(files)

def push_file(filepath):
    """Push a single file to GitHub."""
    abs_path = BASE_DIR / filepath
    if not abs_path.exists():
        print(f"  SKIP: {filepath} (not found)")
        return False
    
    # Read file content
    with open(abs_path, 'rb') as f:
        content = f.read()
    
    # Base64 encode
    import base64
    content_b64 = base64.b64encode(content).decode('utf-8')
    
    # Prepare JSON payload
    payload = {
        "message": f"Add {filepath}",
        "content": content_b64,
        "branch": BRANCH
    }
    
    # Use gh CLI to push
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{REPO_OWNER}/{REPO_NAME}/contents/{filepath}",
             "--method", "PUT",
             "-H", "Accept: application/vnd.github.v3+json",
             "-f", f"message={payload['message']}",
             "-f", f"content={payload['content']}",
             "-f", f"branch={payload['branch']}"],
            capture_output=True, text=True, timeout=60
        )
        
        if result.returncode == 0:
            print(f"  ✓ {filepath}")
            return True
        else:
            # Check if file already exists
            if "already_exists" in result.stderr or "409" in result.stderr:
                print(f"  √ {filepath} (already exists)")
                return True
            print(f"  ✗ {filepath}: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"  ✗ {filepath}: {str(e)}")
        return False

def main():
    print("Getting GitHub file list...")
    github_files = get_github_file_list()
    print(f"Found {len(github_files)} files in GitHub")
    
    print("\nGetting local file list...")
    local_files = get_local_file_list()
    print(f"Found {len(local_files)} local files")
    
    # Find files to push
    files_to_push = sorted(local_files - github_files)
    print(f"\n{len(files_to_push)} files to push")
    
    # Push files in batches
    BATCH_SIZE = 5
    for i in range(0, len(files_to_push), BATCH_SIZE):
        batch = files_to_push[i:i+BATCH_SIZE]
        print(f"\nPushing batch {i//BATCH_SIZE + 1}/{(len(files_to_push)+BATCH_SIZE-1)//BATCH_SIZE}...")
        for filepath in batch:
            push_file(filepath)
    
    print("\n✓ All files processed!")

if __name__ == "__main__":
    main()
