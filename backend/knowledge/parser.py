"""
File: parser.py

Purpose:
Handles multiple document formats (PDF, DOCX, MD, TXT), extracting their text and metadata,
and applying an intelligent chunking strategy (semantic boundaries + overlap).
"""

<<<<<<< HEAD
import io
import re
from typing import Any
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    pass

try:
    import docx
except ImportError:
    pass
=======
import contextlib
import re
from pathlib import Path
from typing import Any

with contextlib.suppress(ImportError):
    from pypdf import PdfReader

with contextlib.suppress(ImportError):
    import docx
>>>>>>> c952205 (Initial upload of AgentOS code)


class DocumentProcessor:
    def __init__(self, max_chunk_size: int = 1500, overlap: int = 200):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def process(self, file_path: str | Path, source_id: str, file_type: str = None) -> list[dict[str, Any]]:
        path = Path(file_path)
        if not file_type:
            file_type = path.suffix.lower().lstrip(".")
<<<<<<< HEAD
            
        content = ""
        metadata = {"title": path.stem}
        
=======

        content = ""
        metadata = {"title": path.stem}

>>>>>>> c952205 (Initial upload of AgentOS code)
        if file_type == "pdf":
            content, pdf_meta = self._parse_pdf(path)
            metadata.update(pdf_meta)
        elif file_type == "docx":
            content, docx_meta = self._parse_docx(path)
            metadata.update(docx_meta)
        elif file_type in ["md", "markdown", "txt"]:
            content = path.read_text(encoding="utf-8")
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
<<<<<<< HEAD
            
        return self._chunk_content(content, source_id, metadata)
        
=======

        return self._chunk_content(content, source_id, metadata)

>>>>>>> c952205 (Initial upload of AgentOS code)
    def _parse_pdf(self, path: Path) -> tuple[str, dict]:
        reader = PdfReader(str(path))
        text_parts = []
        for i, page in enumerate(reader.pages):
            text_parts.append(f"--- Page {i+1} ---\n" + (page.extract_text() or ""))
<<<<<<< HEAD
            
=======

>>>>>>> c952205 (Initial upload of AgentOS code)
        meta = {}
        if reader.metadata:
            meta["title"] = reader.metadata.title or path.stem
            meta["author"] = reader.metadata.author
<<<<<<< HEAD
            
        return "\n\n".join(text_parts), meta
        
=======

        return "\n\n".join(text_parts), meta

>>>>>>> c952205 (Initial upload of AgentOS code)
    def _parse_docx(self, path: Path) -> tuple[str, dict]:
        doc = docx.Document(str(path))
        text_parts = []
        for p in doc.paragraphs:
            text_parts.append(p.text)
<<<<<<< HEAD
            
=======

>>>>>>> c952205 (Initial upload of AgentOS code)
        meta = {
            "title": doc.core_properties.title or path.stem,
            "author": doc.core_properties.author,
            "created": str(doc.core_properties.created) if doc.core_properties.created else None
        }
        return "\n".join(text_parts), meta
<<<<<<< HEAD
        
=======

>>>>>>> c952205 (Initial upload of AgentOS code)
    def _chunk_content(self, text: str, source_id: str, metadata: dict) -> list[dict[str, Any]]:
        # Intelligent chunking: split by paragraphs/double newlines first
        paragraphs = re.split(r'\n{2,}', text)
        chunks = []
        current_chunk = ""
        chunk_idx = 0
<<<<<<< HEAD
        
=======

>>>>>>> c952205 (Initial upload of AgentOS code)
        for p in paragraphs:
            para = p.strip()
            if not para:
                continue
<<<<<<< HEAD
                
            if len(current_chunk) + len(para) > self.max_chunk_size and current_chunk:
                chunks.append(self._create_chunk(current_chunk, source_id, metadata, chunk_idx))
                chunk_idx += 1
                
=======

            if len(current_chunk) + len(para) > self.max_chunk_size and current_chunk:
                chunks.append(self._create_chunk(current_chunk, source_id, metadata, chunk_idx))
                chunk_idx += 1

>>>>>>> c952205 (Initial upload of AgentOS code)
                # Overlap logic
                overlap_text = current_chunk[-self.overlap:] if self.overlap > 0 else ""
                space_idx = overlap_text.find(" ")
                if space_idx != -1:
                    overlap_text = overlap_text[space_idx+1:]
                current_chunk = overlap_text + "\n\n" + para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
<<<<<<< HEAD
                    
        if current_chunk:
            chunks.append(self._create_chunk(current_chunk, source_id, metadata, chunk_idx))
            
        return chunks
        
=======

        if current_chunk:
            chunks.append(self._create_chunk(current_chunk, source_id, metadata, chunk_idx))

        return chunks

>>>>>>> c952205 (Initial upload of AgentOS code)
    def _create_chunk(self, content: str, source_id: str, metadata: dict, index: int) -> dict:
        return {
            "content": content,
            "sourceId": source_id,
            "metadata": metadata,
            "chunkIndex": index
        }
