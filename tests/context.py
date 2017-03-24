import os
import sys


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

TOP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
COMP_PATH = os.path.join(TOP_DIR, 'tests', 'complete_parsed.tsv')
PARTIAL_PATH = os.path.join(TOP_DIR, 'tests', 'incomplete.tsv')
