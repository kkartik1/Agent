# Agent
This multi-agent data visualization system takes the following approach:

**Web Interface:** A Flask-based UI allows users to upload Excel/CSV files and specify visualization requirements in natural language.

**Schema Mapping Agent:** Maps technical column names to business entities using Llama through Ollama, maintaining a knowledge base to improve over time.

**Data Processing Agent:** Interprets natural language requirements and converts them to data operations, applying filters, grouping, and aggregation as needed.
