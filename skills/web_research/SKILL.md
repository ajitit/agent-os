# Web Research Skill

## Purpose

This skill enables agents to perform web research by searching the internet and retrieving relevant documents. Use it when the user or task requires:

- Finding current information
- Looking up facts, statistics, or news
- Comparing products or services
- Gathering sources for reports

## Instructions

1. **Formulate the query**: Create a focused search query from the user's goal.
2. **Execute search**: Use the `web_search` tool (see `resources/tools.py`).
3. **Evaluate results**: Filter for relevance and recency.
4. **Synthesize**: Summarize findings and cite sources.

## Resources

- `resources/tools.py` - Example tool integration pattern
- `resources/prompts.md` - Suggested prompt templates

## Framework Note

This skill is framework-agnostic. Integrate with your preferred AI stack (LangChain, LlamaIndex, raw API, etc.) by implementing the tools referenced in resources.
