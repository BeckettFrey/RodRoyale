"""
Test runner and utilities for Rod Royale API test suite
Run all tests with: python -m pytest tests/ -v
Run specific test file: python -m pytest tests/test_auth.py -v
Run with coverage: python -m pytest tests/ --cov=. --cov-report=html
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_all_tests():
    """Run the complete test suite."""
    import subprocess
    
    # Change to project directory
    os.chdir(project_root)
    
    # Run tests with verbose output
    result = subprocess.run([
        "python", "-m", "pytest", 
        "tests/", 
        "-v",
        "--tb=short",
        "--durations=10"
    ], capture_output=True, text=True)
    
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    print("Return code:", result.returncode)
    
    return result.returncode == 0

def run_specific_test_file(test_file):
    """Run a specific test file."""
    import subprocess
    
    os.chdir(project_root)
    
    result = subprocess.run([
        "python", "-m", "pytest", 
        f"tests/{test_file}", 
        "-v",
        "--tb=short"
    ], capture_output=True, text=True)
    
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    
    return result.returncode == 0

def run_with_coverage():
    """Run tests with coverage report."""
    import subprocess
    
    os.chdir(project_root)
    
    result = subprocess.run([
        "python", "-m", "pytest", 
        "tests/", 
        "--cov=.",
        "--cov-report=html",
        "--cov-report=term-missing",
        "-v"
    ], capture_output=True, text=True)
    
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    
    return result.returncode == 0

if __name__ == "__main__":
    print("Rod Royale API Test Suite")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "all":
            print("Running all tests...")
            success = run_all_tests()
        elif command == "coverage":
            print("Running tests with coverage...")
            success = run_with_coverage()
        elif command.startswith("test_"):
            print(f"Running {command}...")
            success = run_specific_test_file(command)
        else:
            print(f"Unknown command: {command}")
            print("Available commands: all, coverage, test_auth.py, test_users.py, etc.")
            sys.exit(1)
    else:
        print("Running all tests...")
        success = run_all_tests()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
