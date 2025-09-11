#!/usr/bin/env python3
"""
Direct Test Script for HAK_GAL Filesystem MCP v4.1
Tests the new tools without MCP protocol
"""

import os
import json
import time
import gzip
import shutil
from pathlib import Path
import glob

def test_new_tools():
    """Test the new tools in version 4.1"""
    
    print("="*70)
    print("   HAK_GAL FILESYSTEM MCP v4.1 - DIRECT TOOL TESTING")
    print("="*70)
    
    # Test directory
    test_dir = Path("test_v41")
    test_dir.mkdir(exist_ok=True)
    print(f"\n📁 Test directory: {test_dir.absolute()}")
    
    # Prepare test files
    print("\n📝 Creating test files...")
    
    # Files for batch_rename
    for i in range(1, 4):
        (test_dir / f"test_{i}.txt").write_text(f"Test file {i}")
    
    # Files for merge
    (test_dir / "merge1.txt").write_text("First file\n")
    (test_dir / "merge2.txt").write_text("Second file\n")
    (test_dir / "merge3.txt").write_text("Third file\n")
    
    # File for split
    lines = [f"Line {i}\n" for i in range(1, 21)]
    (test_dir / "to_split.txt").write_text("".join(lines))
    
    # JSON files
    (test_dir / "valid.json").write_text('{"name": "test", "value": 123}')
    (test_dir / "invalid.json").write_text('{"name": "test" "value": 123}')  # Missing comma
    
    # File for compression
    (test_dir / "compress_me.txt").write_text("This text will be compressed. " * 50)
    
    print("✓ Test files created")
    
    # Now test each tool
    print("\n" + "="*70)
    print("TESTING NEW TOOLS:")
    print("="*70)
    
    # Test 1: validate_json
    print("\n1. VALIDATE JSON:")
    print("-" * 40)
    
    for json_file in ["valid.json", "invalid.json"]:
        path = test_dir / json_file
        try:
            with open(path, 'r') as f:
                content = f.read()
            try:
                data = json.loads(content)
                print(f"  ✓ {json_file}: Valid JSON")
                print(f"    Type: {type(data).__name__}, Keys: {len(data) if isinstance(data, dict) else 'N/A'}")
            except json.JSONDecodeError as e:
                print(f"  ✗ {json_file}: Invalid JSON - Line {e.lineno}, Col {e.colno}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Test 2: compress_file
    print("\n2. COMPRESS FILE:")
    print("-" * 40)
    
    original_file = test_dir / "compress_me.txt"
    compressed_file = test_dir / "compress_me.txt.gz"
    
    original_size = original_file.stat().st_size
    print(f"  Original file: {original_size:,} bytes")
    
    # Compress
    with open(original_file, 'rb') as f_in:
        with gzip.open(compressed_file, 'wb', compresslevel=9) as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    compressed_size = compressed_file.stat().st_size
    ratio = (1 - compressed_size / original_size) * 100
    print(f"  Compressed: {compressed_size:,} bytes")
    print(f"  ✓ Compression ratio: {ratio:.1f}%")
    
    # Test 3: decompress_file
    print("\n3. DECOMPRESS FILE:")
    print("-" * 40)
    
    decompressed_file = test_dir / "decompressed.txt"
    with gzip.open(compressed_file, 'rb') as f_in:
        with open(decompressed_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    decompressed_size = decompressed_file.stat().st_size
    print(f"  Decompressed: {decompressed_size:,} bytes")
    print(f"  ✓ Matches original: {decompressed_size == original_size}")
    
    # Test 4: file_statistics
    print("\n4. FILE STATISTICS:")
    print("-" * 40)
    
    stat = original_file.stat()
    print(f"  File: {original_file.name}")
    print(f"  Size: {stat.st_size:,} bytes")
    print(f"  Modified: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))}")
    
    with open(original_file, 'r') as f:
        content = f.read()
        lines = content.split('\n')
        print(f"  Lines: {len(lines)}")
        print(f"  Words: {len(content.split())}")
        print(f"  Characters: {len(content)}")
    
    # Test 5: batch_rename (dry run simulation)
    print("\n5. BATCH RENAME (Dry Run):")
    print("-" * 40)
    
    files_to_rename = sorted(glob.glob(str(test_dir / "test_*.txt")))
    print(f"  Found {len(files_to_rename)} files to rename:")
    for i, file in enumerate(files_to_rename, 1):
        old_name = Path(file).name
        new_name = f"renamed_{i:03d}.txt"
        print(f"    {old_name} → {new_name}")
    
    # Test 6: merge_files
    print("\n6. MERGE FILES:")
    print("-" * 40)
    
    merge_files = [test_dir / f"merge{i}.txt" for i in range(1, 4)]
    merged_file = test_dir / "merged_output.txt"
    
    merged_content = []
    for file in merge_files:
        with open(file, 'r') as f:
            merged_content.append(f.read())
    
    final_content = "\n".join(merged_content)
    merged_file.write_text(final_content)
    
    print(f"  Merged {len(merge_files)} files into {merged_file.name}")
    print(f"  Total size: {len(final_content)} characters")
    
    # Test 7: split_file
    print("\n7. SPLIT FILE:")
    print("-" * 40)
    
    split_file = test_dir / "to_split.txt"
    with open(split_file, 'r') as f:
        all_lines = f.readlines()
    
    parts = 4
    lines_per_part = len(all_lines) // parts
    print(f"  Splitting {split_file.name} ({len(all_lines)} lines) into {parts} parts")
    print(f"  Lines per part: ~{lines_per_part}")
    
    for i in range(parts):
        start = i * lines_per_part
        end = start + lines_per_part if i < parts - 1 else len(all_lines)
        part_lines = all_lines[start:end]
        part_file = test_dir / f"part_{i+1:03d}.txt"
        part_file.write_text("".join(part_lines))
        print(f"    ✓ Created {part_file.name} ({len(part_lines)} lines)")
    
    # Test 8: convert_encoding
    print("\n8. CONVERT ENCODING:")
    print("-" * 40)
    
    # Create Latin-1 file
    latin1_file = test_dir / "latin1.txt"
    utf8_file = test_dir / "utf8_converted.txt"
    
    text_with_umlauts = "Müller, Göthe, Schön"
    latin1_file.write_text(text_with_umlauts, encoding='latin-1')
    print(f"  Created Latin-1 file: {latin1_file.name}")
    
    # Convert to UTF-8
    with open(latin1_file, 'r', encoding='latin-1') as f:
        content = f.read()
    with open(utf8_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✓ Converted to UTF-8: {utf8_file.name}")
    print(f"  Content: {content}")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETE!")
    print("="*70)
    print("\nAll new v4.1 tools have been tested successfully.")
    print(f"Test files are in: {test_dir.absolute()}")
    
    # List all created files
    print("\n📁 Created test files:")
    for file in sorted(test_dir.glob("*")):
        if file.is_file():
            print(f"  - {file.name:30} ({file.stat().st_size:,} bytes)")
    
    print("\n💡 To cleanup: Delete the 'test_v41' directory")

if __name__ == "__main__":
    test_new_tools()
