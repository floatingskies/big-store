#!/usr/bin/env python3
"""
Big Store - Main Executable
Loja de Aplicativos Linux moderna e completa
"""

import sys
import os

# Add the package to path if running from source
script_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(script_dir, 'big_store')):
    sys.path.insert(0, script_dir)

from big_store.main import main

if __name__ == '__main__':
    sys.exit(main())
