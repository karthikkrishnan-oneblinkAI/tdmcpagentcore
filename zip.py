#!/usr/bin/env python
"""
A simple zip utility wrapper for Windows to work with agentcore
Usage: python zip.py -r output.zip folder/
"""
import sys
import zipfile
import os
from pathlib import Path

def create_zip(output_file, source_path, recursive=False):
    """Create a zip file from source path"""
    source = Path(source_path)
    
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if source.is_file():
            zipf.write(source, source.name)
        elif source.is_dir():
            if recursive:
                for root, dirs, files in os.walk(source):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(source.parent)
                        zipf.write(file_path, arcname)
            else:
                for file in source.iterdir():
                    if file.is_file():
                        zipf.write(file, file.name)

def main():
    if len(sys.argv) < 3:
        print("Usage: zip.py [-r] output.zip source")
        sys.exit(1)
    
    recursive = False
    args = sys.argv[1:]
    
    if '-r' in args:
        recursive = True
        args.remove('-r')
    
    if len(args) < 2:
        print("Usage: zip.py [-r] output.zip source")
        sys.exit(1)
    
    output_file = args[0]
    source_path = args[1]
    
    create_zip(output_file, source_path, recursive)
    print(f"Created {output_file}")

if __name__ == "__main__":
    main()
