## Agentic GraphRAG E-Commerce Engine

An autonomous Retrieval-Augmented Generation (RAG) system capable of intelligent query routing. Built with LangChain and Gemini, this system dynamically routes multi-hop queries between a local Vector Database (for unstructured semantic search) and a cloud Knowledge Graph (for structured deterministic filtering).

## System Architecture

The core of this engine is a LangChain **ReAct Agent** that uses prompt-driven query expansion to decide which database to call based on user intent.

1. **Unstructured Pipeline (Policies & SLAs):** Uses local Hugging Face Bi-Encoders (`all-MiniLM-L6-v2`) to embed text, retrieved via **Qdrant** using HNSW approximate nearest neighbor search.
2. **Structured Pipeline (Product Catalog):** Uses **Neo4j** index-free adjacency to instantly traverse a dense, synthetic 5,000-node Knowledge Graph via parameterized Cypher queries.
3. **Orchestration & UI:** Managed by LangChain's state graph and deployed via a conversational **Streamlit** frontend.

## Evaluation Metrics
The system's reasoning and retrieval pipelines were rigorously evaluated using the **Ragas** (LLM-as-a-Judge) framework against a golden ground-truth dataset, achieving:
* **Context Precision:** 88%
* **Faithfulness (Hallucination Prevention):** 92%
* **Answer Relevance:** 94%

## Repository Structure
```text
├── app.py                      # Streamlit frontend & session state
├── generate_catalog.py         # Synthetic Knowledge Graph generator (Faker + Cypher UNWIND)
├── evaluate_agent.py           # Ragas evaluation pipeline script
├── indexing/
│   └── ingest_policies.py      # Semantic chunking and local Qdrant ingestion
└── retrieval_agent/
    ├── agent.py                # LangChain ReAct agent and LLM initialization
    └── tools.py                # Database connection tools and Agentic routing prompts