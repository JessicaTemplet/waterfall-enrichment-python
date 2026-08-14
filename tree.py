import os

# Folders to completely ignore
EXCLUDE_DIRS = {
    'venv', '.venv', 'env', 'target', '__pycache__', '.git', 
    'node_modules', 'dist', 'build', 'instance', 'postgres_data', 
    'mysql_data', 'redis_data', '.idea', '.vscode'
}

# File extensions to ignore (Weights, DBs, Caches)
EXCLUDE_EXTS = {
    # Model weights & binary artifacts
    '.pt', '.pth', '.bin', '.safetensors', '.onnx', '.pyc', '.exe',
    # Database files
    '.db', '.sqlite', '.sqlite3', '.db3', '.s3db', '.mdf', '.ldf', '.dump', '.rdb', '.sql'
}

def print_tree(start_dir='.'):
    for root, dirs, files in os.walk(start_dir):
        # Prune ignored directories in-place so os.walk doesn't dive into them
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        # Calculate depth for visual indentation
        rel_path = os.path.relpath(root, start_dir)
        if rel_path == '.':
            depth = 0
            print(f"├── {os.path.basename(os.path.abspath(start_dir))}/")
        else:
            depth = rel_path.count(os.sep) + 1
            indent = "│   " * (depth - 1)
            print(f"{indent}├── {os.path.basename(root)}/")
        
        sub_indent = "│   " * depth
        for file in files:
            if not any(file.endswith(ext) for ext in EXCLUDE_EXTS):
                print(f"{sub_indent}├── {file}")

if __name__ == '__main__':
    print_tree('.')