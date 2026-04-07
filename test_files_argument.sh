#!/bin/bash

# Test script for --files argument functionality

WIKI_DIR="./wiki"
TEST_FILE1="$WIKI_DIR/test1.md"
TEST_FILE2="$WIKI_DIR/test2.md"

# Test 1: Basic --files functionality
echo "Test 1: Basic --files functionality"
OUTPUT1=$(python3 scripts/wiki_weaver.py --wiki "$WIKI_DIR" --files "test1.md,test2.md" 2>&1)
if [[ $OUTPUT1 == *"处理 2 份指定文档"* ]]; then
    echo "✅ Test 1 PASSED: Correctly processed 2 files"
else
    echo "❌ Test 1 FAILED: Expected to process 2 files"
    echo "Output: $OUTPUT1"
fi

# Test 2: --files with relative paths
echo ""
echo "Test 2: --files with relative paths"
OUTPUT2=$(python3 scripts/wiki_weaver.py --wiki "$WIKI_DIR" --files "./test1.md,./test2.md" 2>&1)
if [[ $OUTPUT2 == *"处理 2 份指定文档"* ]]; then
    echo "✅ Test 2 PASSED: Correctly processed files with relative paths"
else
    echo "❌ Test 2 FAILED: Expected to process files with relative paths"
    echo "Output: $OUTPUT2"
fi

# Test 3: --files with query combination
echo ""
echo "Test 3: --files with query combination"
OUTPUT3=$(python3 scripts/wiki_weaver.py --wiki "$WIKI_DIR" --files "test1.md" --query "test" 2>&1)
if [[ $OUTPUT3 == *"处理 1 份指定文档"* ]]; then
    echo "✅ Test 3 PASSED: Correctly combined --files with --query"
else
    echo "❌ Test 3 FAILED: Expected to process 1 file with query filter"
    echo "Output: $OUTPUT3"
fi

# Test 4: Invalid file handling
echo ""
echo "Test 4: Invalid file handling"
OUTPUT4=$(python3 scripts/wiki_weaver.py --wiki "$WIKI_DIR" --files "nonexistent.md,test1.md" 2>&1)
if [[ $OUTPUT4 == *"警告: 文件不存在或不是Markdown文件"* && $OUTPUT4 == *"处理 1 份指定文档"* ]]; then
    echo "✅ Test 4 PASSED: Correctly handled invalid file and processed valid one"
else
    echo "❌ Test 4 FAILED: Expected warning for invalid file and processing of valid file"
    echo "Output: $OUTPUT4"
fi

echo ""
echo "All tests completed!"

