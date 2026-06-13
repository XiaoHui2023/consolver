"""PyInstaller runtime hook: point Z3 at bundled native libraries."""

from __future__ import annotations

import builtins
import os
import sys

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    builtins.Z3_LIB_DIRS = [os.path.join(sys._MEIPASS, "z3", "lib")]
