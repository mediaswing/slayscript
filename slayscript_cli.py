#!/usr/bin/env python3
"""Entry point for PyInstaller builds."""

import sys
import os

# Ensure the package directory is in the path for PyInstaller builds
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    bundle_dir = sys._MEIPASS
    sys.path.insert(0, bundle_dir)

from slayscript.main import main

if __name__ == "__main__":
    main()
