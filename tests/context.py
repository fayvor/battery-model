"""
Context for tests. Modifies sys.path to add relative path to the main module.
See: https://docs.python-guide.org/writing/structure/
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import battery
