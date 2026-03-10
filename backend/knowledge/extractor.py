"""
File: extractor.py

Purpose:
Extracts code blocks from text (web crawls or parsed docs) and stores them 
in a structured way, deduping via hashing and capturing preceding context.
"""

import hashlib
import re
from typing import Any

class CodeExtractor:
    def __init__(self):
        # Regex to find standard Markdown fenced code blocks
        # Captures up to 3 preceding lines of context
        self.code_pattern = re.compile(r'(?P<context>(?:[^\n]+\n){1,3})?```(?P<lang>[\w\-+#]*)\n(?P<code>.*?)```', re.DOTALL)
        self.seen_hashes = set()

    def extract(self, text: str, source_id: str) -> list[dict[str, Any]]:
        results = []
        matches = self.code_pattern.finditer(text)
        
        for match in matches:
            code = match.group("code").strip()
            if not code:
                continue
                
            lang = match.group("lang").strip() or "unknown"
            context = match.group("context")
            # Clean up context to be a short description
            description = (context or "").strip().replace('\n', ' ')
            
            code_hash = hashlib.sha256(code.encode('utf-8')).hexdigest()
            if code_hash in self.seen_hashes:
                continue
                
            self.seen_hashes.add(code_hash)
            
            line_count = len(code.splitlines())
            results.append({
                "sourceId": source_id,
                "language": lang,
                "code": code,
                "description": description[:200] + ("..." if len(description) > 200 else ""),
                "lineCount": line_count,
                "hash": code_hash
            })
            
        return results
