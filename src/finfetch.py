#!/usr/bin/env python3
"""
FinFetch entry point script.
"""

import sys
import os
import click

# Add current directory to path (we're already in src/)
sys.path.insert(0, os.path.dirname(__file__))

# Import only the CLI module directly
from cli import cli

if __name__ == "__main__":
    cli()
