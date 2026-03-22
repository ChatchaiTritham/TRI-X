"""Command-line interface for TRI-X."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def demo() -> None:
    """Run the TRI-X demo script."""
    from scripts.demo import main

    main()


def validate() -> None:
    """Run TRI-X tests."""
    import pytest

    test_directory = Path(__file__).parent.parent / "tests"
    sys.exit(pytest.main([str(test_directory), "-v"]))


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="TRI-X Framework CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.add_parser("demo", help="Run TRI-X demo")
    subparsers.add_parser("validate", help="Run validation tests")

    parsed_args = parser.parse_args()
    if parsed_args.command == "demo":
        demo()
    elif parsed_args.command == "validate":
        validate()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
