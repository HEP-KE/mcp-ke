#!/usr/bin/env python3
"""
Test script for path utilities - ensures input/output directory handling works correctly.
"""

import os
import sys
import tempfile
import shutil

# Add the tools directory to the path
tools_path = os.path.join(os.path.dirname(__file__), 'tools')
sys.path.insert(0, tools_path)

from path_utils import get_input_path, get_output_path


def test_input_path():
    """Test get_input_path function."""
    print("Testing get_input_path()...")

    # Create a temporary directory to simulate user's working directory
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()

        try:
            # Change to temp directory
            os.chdir(tmpdir)

            # Test 1: No input directory - should raise error
            print("\n  Test 1: No input directory...")
            try:
                get_input_path("data.txt")
                print("    FAILED: Should have raised FileNotFoundError")
                return False
            except FileNotFoundError as e:
                print(f"    PASSED: {e}")

            # Test 2: Create input directory and file
            print("\n  Test 2: Input directory with file...")
            os.makedirs("input", exist_ok=True)
            test_file = os.path.join("input", "test_data.txt")
            with open(test_file, 'w') as f:
                f.write("test data")

            result = get_input_path("test_data.txt")
            expected = os.path.join(tmpdir, "input", "test_data.txt")
            if result == expected:
                print(f"    PASSED: {result}")
            else:
                print(f"    FAILED: Expected {expected}, got {result}")
                return False

            # Test 3: File not in input directory
            print("\n  Test 3: File not in input directory...")
            try:
                get_input_path("nonexistent.txt")
                print("    FAILED: Should have raised FileNotFoundError")
                return False
            except FileNotFoundError as e:
                print(f"    PASSED: {e}")

            # Test 4: Absolute path (bypass input/ directory)
            print("\n  Test 4: Absolute path...")
            abs_file = os.path.join(tmpdir, "absolute_data.txt")
            with open(abs_file, 'w') as f:
                f.write("absolute data")

            result = get_input_path(abs_file)
            if result == abs_file:
                print(f"    PASSED: {result}")
            else:
                print(f"    FAILED: Expected {abs_file}, got {result}")
                return False

            print("\n✓ All input path tests passed!")
            return True

        finally:
            os.chdir(original_cwd)


def test_output_path():
    """Test get_output_path function."""
    print("\n\nTesting get_output_path()...")

    # Create a temporary directory to simulate user's working directory
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()

        try:
            # Change to temp directory
            os.chdir(tmpdir)

            # Test 1: No out directory - should raise error
            print("\n  Test 1: No out directory...")
            try:
                get_output_path("result.png")
                print("    FAILED: Should have raised FileNotFoundError")
                return False
            except FileNotFoundError as e:
                print(f"    PASSED: {e}")

            # Test 2: Create out directory
            print("\n  Test 2: Out directory exists...")
            os.makedirs("out", exist_ok=True)

            result = get_output_path("result.png")
            expected = os.path.join(tmpdir, "out", "result.png")
            if result == expected:
                print(f"    PASSED: {result}")
            else:
                print(f"    FAILED: Expected {expected}, got {result}")
                return False

            # Test 3: Absolute path (bypass out/ directory)
            print("\n  Test 3: Absolute path...")
            abs_path = os.path.join(tmpdir, "absolute_result.png")
            result = get_output_path(abs_path)
            if result == abs_path:
                print(f"    PASSED: {result}")
            else:
                print(f"    FAILED: Expected {abs_path}, got {result}")
                return False

            # Test 4: None input
            print("\n  Test 4: None input...")
            result = get_output_path(None)
            if result is None:
                print(f"    PASSED: returned None")
            else:
                print(f"    FAILED: Expected None, got {result}")
                return False

            print("\n✓ All output path tests passed!")
            return True

        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    print("=" * 60)
    print("PATH UTILITIES TEST SUITE")
    print("=" * 60)

    success = True
    success = test_input_path() and success
    success = test_output_path() and success

    print("\n" + "=" * 60)
    if success:
        print("✓ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("✗ SOME TESTS FAILED")
        sys.exit(1)
