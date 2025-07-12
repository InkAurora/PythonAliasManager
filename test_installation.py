#!/usr/bin/env python3
"""
Test script for Python Alias Manager installations.
Verifies that the modular package structure works correctly.
"""

import subprocess
import sys
import tempfile
import os
from pathlib import Path


def run_command(cmd, check=True):
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=check, 
            capture_output=True, 
            text=True
        )
        return True, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr


def test_import():
    """Test that the package can be imported."""
    print("Testing package import...")
    try:
        import alias_manager
        print("✅ Package import successful")
        return True
    except ImportError as e:
        print(f"❌ Package import failed: {e}")
        return False


def test_module_execution():
    """Test running the package as a module."""
    print("Testing module execution...")
    success, stdout, stderr = run_command("python -m alias_manager --help")
    if success:
        print("✅ Module execution successful")
        return True
    else:
        print(f"❌ Module execution failed: {stderr}")
        return False


def test_entry_point():
    """Test the pam entry point."""
    print("Testing entry point command...")
    success, stdout, stderr = run_command("pam --help", check=False)
    if success:
        print("✅ Entry point 'pam' working")
        return True
    else:
        print("⚠️  Entry point 'pam' not found in PATH")
        print("   This is normal if not installed with pip")
        return False


def test_basic_functionality():
    """Test basic functionality with a temporary alias."""
    print("Testing basic functionality...")
    
    # Create a temporary Python script in the same directory as this test
    test_dir = Path(__file__).parent
    test_script = test_dir / "temp_test_script.py"
    
    try:
        # Create temporary test script
        with open(test_script, 'w') as f:
            f.write('#!/usr/bin/env python3\nimport sys\nprint("Hello from test script!")\n')
        
        # Try to add an alias - just check that the command succeeds
        script_path = str(test_script.absolute()).replace('\\', '/')
        cmd = f'python -m alias_manager add test_alias "{script_path}"'
        success, stdout, stderr = run_command(cmd)
        if not success:
            print(f"❌ Failed to add test alias: {stderr}")
            print(f"Command was: {cmd}")
            return False
        
        # Try to list aliases - just check that the command succeeds
        success, stdout, stderr = run_command("python -m alias_manager list")
        if not success:
            print(f"❌ Failed to list aliases: {stderr}")
            return False
        
        # Try to remove the test alias - check that command succeeds
        success, stdout, stderr = run_command("python -m alias_manager remove test_alias")
        if not success:
            print(f"❌ Failed to remove test alias: {stderr}")
            return False
        
        print("✅ Basic functionality test passed (commands executed successfully)")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
        
    finally:
        # Clean up
        if test_script.exists():
            test_script.unlink()
        # Also try to clean up any alias that might have been created
        run_command("python -m alias_manager remove test_alias", check=False)


def test_all_modules():
    """Test that all modules can be imported."""
    print("Testing all module imports...")
    modules = [
        'alias_manager.core',
        'alias_manager.cli',
        'alias_manager.config',
        'alias_manager.venv_detector',
        'alias_manager.script_generator',
        'alias_manager.dependency_manager',
        'alias_manager.environment_setup'
    ]
    
    failed_modules = []
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            failed_modules.append(module)
    
    if not failed_modules:
        print("✅ All modules imported successfully")
        return True
    else:
        print(f"❌ Failed to import {len(failed_modules)} modules")
        return False


def main():
    """Run all tests."""
    print("Python Alias Manager - Installation Test")
    print("=" * 40)
    
    tests = [
        ("Package Import", test_import),
        ("Module Imports", test_all_modules),
        ("Module Execution", test_module_execution),
        ("Entry Point", test_entry_point),
        ("Basic Functionality", test_basic_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print(f"\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Installation is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
