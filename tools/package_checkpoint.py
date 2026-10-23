#!/usr/bin/env python3
"""Compatibility entry point: checkpoints are now code-only source archives."""
import sys
from package_source import main
if __name__=="__main__":
    if len(sys.argv)>1 and sys.argv[1].isdigit():sys.argv.pop(1)
    main()
