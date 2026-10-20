"""Test package bootstrap: put the repository's src/ on sys.path.

This makes `python -m unittest discover` work from the repository root
without installing the package.
"""

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC = os.path.join(_ROOT, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
