# Knowledge Management

This skill provides powerful Retrieval-Augmented Generation (RAG) capabilities to the agent.
It allows you to:
1. Search the internal knowledge base for factual grounding, retrieved code examples, or documentation.
2. Ingest new knowledge sources (Web URLs, PDFs, DOCX files) directly into the vector database.
3. List the current knowledge sources available to you.

## Instructions
When a user asks you questions that require external documentation or context, use `knowledge_search`.
If the user provides a link or a file and asks you to "learn" or "remember" it, use `knowledge_ingest`.

## Tools
* **`knowledge_search`**: Use this to perform hybrid semantic/keyword searches.
* **`knowledge_ingest`**: Use this to command the background system to crawl a webpage or parse a document.
* **`knowledge_list_sources`**: Use this to see what sources have already been indexed.
