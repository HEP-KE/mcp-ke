#!/usr/bin/env python3
"""
Test script for agent helper tools - ensures they work with out/ directory.
"""

import os
import sys
import tempfile
import numpy as np

# Add the tools directory to the path
tools_path = os.path.join(os.path.dirname(__file__), 'tools')
sys.path.insert(0, tools_path)

from agent_helper_tools import (
    list_agent_files,
    save_array,
    load_array,
    save_dict,
    load_dict,
)


def test_agent_helper_tools():
    """Test agent helper tools with out/ directory."""
    print("Testing agent helper tools...")

    # Create a temporary directory to simulate user's working directory
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()

        try:
            # Change to temp directory
            os.chdir(tmpdir)

            # Test 1: No out directory - should raise error
            print("\n  Test 1: No out directory...")
            try:
                list_agent_files()
                print("    FAILED: Should have raised FileNotFoundError")
                return False
            except FileNotFoundError as e:
                print(f"    PASSED: {e}")

            # Create out directory
            os.makedirs("out", exist_ok=True)

            # Test 2: List files in empty directory
            print("\n  Test 2: List files in empty directory...")
            files = list_agent_files()
            if len(files) == 0:
                print(f"    PASSED: Empty directory")
            else:
                print(f"    FAILED: Expected 0 files, got {len(files)}")
                return False

            # Test 3: Save and load array
            print("\n  Test 3: Save and load array...")
            test_array = np.array([1, 2, 3, 4, 5])
            saved_path = save_array(test_array, "test_array.npy")
            if os.path.exists(saved_path):
                print(f"    PASSED: Array saved to {os.path.basename(saved_path)}")
            else:
                print(f"    FAILED: File not created")
                return False

            loaded_array = load_array("test_array.npy")
            if np.array_equal(test_array, loaded_array):
                print(f"    PASSED: Array loaded correctly")
            else:
                print(f"    FAILED: Loaded array doesn't match")
                return False

            # Test 4: Save and load dict
            print("\n  Test 4: Save and load dict...")
            test_dict = {
                'array1': np.array([10, 20, 30]),
                'array2': np.array([40, 50, 60]),
                'value': 42,
                'name': 'test'
            }
            saved_path = save_dict(test_dict, "test_dict.json")
            if os.path.exists(saved_path):
                print(f"    PASSED: Dict saved to {os.path.basename(saved_path)}")
            else:
                print(f"    FAILED: File not created")
                return False

            loaded_dict = load_dict("test_dict")
            if (np.array_equal(test_dict['array1'], loaded_dict['array1']) and
                np.array_equal(test_dict['array2'], loaded_dict['array2']) and
                test_dict['value'] == loaded_dict['value'] and
                test_dict['name'] == loaded_dict['name']):
                print(f"    PASSED: Dict loaded correctly")
            else:
                print(f"    FAILED: Loaded dict doesn't match")
                return False

            # Test 5: List all files
            print("\n  Test 5: List all files...")
            files = list_agent_files()
            # Should have: test_array.npy, test_dict_array1.npy, test_dict_array2.npy, test_dict_metadata.json
            if len(files) >= 4:
                print(f"    PASSED: Found {len(files)} files")
            else:
                print(f"    FAILED: Expected at least 4 files, got {len(files)}")
                return False

            print("\n✓ All agent helper tool tests passed!")
            return True

        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    print("=" * 60)
    print("AGENT HELPER TOOLS TEST SUITE")
    print("=" * 60)

    if test_agent_helper_tools():
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("✗ SOME TESTS FAILED")
        sys.exit(1)
