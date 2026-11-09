"""
Module entrypoint allowing `python -m ad_project`.
"""

import sys
from ad_project.cli import main

if __name__ == "__main__":
    sys.exit(main())
