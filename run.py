#!/usr/bin/env python
"""Entry point for the Patent Drafting Assistant."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    from src.main import main
    main()
