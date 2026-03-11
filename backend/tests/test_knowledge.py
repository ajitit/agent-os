"""
File: test_knowledge.py

Purpose:
Integration and unit tests for the Knowledge Management RAG feature.
"""

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)
API_PREFIX = "/api/v1/knowledge"

def test_add_source_and_list():
    # Add a web source
    resp = client.post(
        f"{API_PREFIX}/sources",
        json={
            "name": "Test Site",
            "type": "web",
            "url": "http://example.com/mock",
            "tags": ["test-tag"]
        }
    )
    assert resp.status_code == 200
    source = resp.json()
    assert source["name"] == "Test Site"
    assert source["type"] == "web"
    sid = source["id"]

    # List sources
    resp = client.get(f"{API_PREFIX}/sources")
    assert resp.status_code == 200
    sources = resp.json()
    assert len(sources) >= 1
    assert any(s["id"] == sid for s in sources)

    # Filter list
    resp = client.get(f"{API_PREFIX}/sources?type=web")
    assert resp.status_code == 200
    sources = resp.json()
    assert any(s["id"] == sid for s in sources)

def test_delete_source():
    # Create for deletion
    resp = client.post(
        f"{API_PREFIX}/sources",
        json={
            "name": "Delete Me",
            "type": "text",
        }
    )
    sid = resp.json()["id"]

    # Delete
    del_resp = client.delete(f"{API_PREFIX}/sources/{sid}")
    assert del_resp.status_code == 200

    # Verify
    list_resp = client.get(f"{API_PREFIX}/sources")
    assert not any(s["id"] == sid for s in list_resp.json())

def test_search_endpoint():
    # Testing search doesn't crash (mock search)
    resp = client.post(
        f"{API_PREFIX}/search",
        json={"query": "test query", "top_k": 2}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data

def test_extract_code_unit():
    from backend.knowledge.extractor import CodeExtractor
    extractor = CodeExtractor()

    sample_text = """
This is some context leading up to the code.
It explains what the code does.
```python
def test_func():
    return 42
```
Some trailing text.
"""
    results = extractor.extract(sample_text, "test_source_id")
    assert len(results) == 1
    code_obj = results[0]
    assert code_obj["language"] == "python"
    assert "def test_func" in code_obj["code"]
    assert "This is some context" in code_obj["description"]
    assert code_obj["lineCount"] == 2

def test_document_processor_chunking():
    from backend.knowledge.parser import DocumentProcessor
    parser = DocumentProcessor(max_chunk_size=100, overlap=10)

    text = (
        "This is the first paragraph. It is somewhat long to test the boundaries. "
        "We need it to split properly.\n\n"
        "This is the second paragraph. It should end up in the second chunk if the size allows."
    )

    chunks = parser._chunk_content(text, "test_id", {"title": "Doc"})
    assert len(chunks) > 0
    assert chunks[0]["sourceId"] == "test_id"
    assert chunks[0]["chunkIndex"] == 0
    assert "title" in chunks[0]["metadata"]
