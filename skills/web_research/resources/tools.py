"""
File: tools.py

Purpose:
Provides a placeholder (Level 3 resource) example of a framework-agnostic tool 
implementation for the Web Research skill.

Key Functionalities:
- Define the `web_search` function signature and basic documentation
- Illustrate how developers should integrate search tools via LangChain, LlamaIndex, or raw APIs

Inputs:
- String search queries

Outputs:
- Dummy list (intended to be list of web search result dictionaries)

Interacting Files / Modules:
- None
"""

# This file demonstrates the resource pattern (Level 3).
# Implement web_search using your preferred framework:
# - LangChain: use WebSearchRun
# - LlamaIndex: use VectorStoreIndex with web loader
# - Raw: call Search API directly

def web_search(query: str) -> list[dict]:
    """
    Placeholder for web search implementation.
    Returns list of {title, snippet, url} dicts.
    """
    # Replace with actual implementation
    return []
