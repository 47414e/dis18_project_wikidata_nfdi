#%%
# Standard libraries that do not need to be installed

# Convenient parsing of command-line arguments.
# argparse

# Simple read/write routines for CSV files.
# csv

# Flexible, thread-safe logging framework.
# logging

# Low-level access to time functions.
# time

# Basic HTTP and URL utilities without external dependencies.
# urllib

# Operating system interface.
# os

# Enables future features (here: postponed evaluation of type hints).
# from __future__ import annotations

# Convenient object-oriented API for file paths.
# from pathlib import Path

# Type hints.
# from typing import Optional, Dict

# Memoization decorator.
# from functools import lru_cache

#%%
# Libraries that need to be installed additionally

# Data processing
# pandas

# HTTP API calls
# requests

# Decode HTTP API JSON responses
# orjson

# Queries, handles URL encoding & HTTP requests
# SPARQLWrapper

#%%
!pip install pandas requests orjson SPARQLWrapper