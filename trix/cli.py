"""
Command-line interface for TRI-X framework.
"""

import argparse
import sys
from pathlib import Path

def demo():
 """Run TRI-X demo"""
 from scripts.demo import main
 main()

def validate():
 """Run validation tests"""
 print("Running TRI-X validation tests...")
 import pytest
 test_dir = Path(__file__).parent.parent / "tests"
 sys.exit(pytest.main([str(test_dir), "-v"]))

def main():
 """Main CLI entry point"""
 parser = argparse.ArgumentParser(description="TRI-X Framework CLI")
 subparsers = parser.add_subparsers(dest="command", help="Available commands")

 # Demo command
 subparsers.add_parser("demo", help="Run TRI-X demo")

 # Validate command
 subparsers.add_parser("validate", help="Run validation tests")

 args = parser.parse_args()

 if args.command == "demo":
 demo()
 elif args.command == "validate":
 validate()
 else:
 parser.print_help()

if __name__ == "__main__":
 main()
