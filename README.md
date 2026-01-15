

## PDF-Based Retrieval-Augmented Generation (RAG)

This project implements an end-to-end Retrieval-Augmented Generation (RAG) pipeline that enables context-aware question answering over PDF documents using semantic search and large language models.

---

### Project Overview

The system loads one or more PDF files, splits their content into manageable text chunks, generates semantic embeddings using Google Gemini embedding models, stores vectors in a Chroma vector database, and performs similarity search to retrieve relevant context. Retrieved context is then passed to a Gemini chat model to produce grounded responses.

This repository serves as a reusable reference implementation for building document-based RAG systems.

---

### Project Structure

```
1.0_RAG_PDF.ipynb        # Main RAG pipeline notebook
Festo_File_Overview.pdf # Sample PDF used for ingestion
Vectorstore/            # Local Chroma vector database
pyproject.toml          # Project dependencies (uv)
uv.lock                 # Locked dependency versions
.env.example            # Example environment variable file
```

---

### Tech Stack

* Python
* LangChain
* Google Gemini Embeddings (`models/embedding-001`)
* Google Gemini Chat Model
* Chroma Vector Database
* PyPDF Document Loader
* uv (Python package manager)

---

### Key Features

* PDF document ingestion and text extraction
* Recursive text chunking with overlap
* Semantic embedding generation using Gemini
* Vector storage using Chroma
* Similarity-based semantic retrieval
* Context-aware question answering
* Scalable design to support **multiple PDF documents**
* Local vector store persistence for reuse across sessions

---

### How to Run

1. Add your Google API key to a `.env` file:

```
GOOGLE_API_KEY=your_api_key_here
```

2. Ensure **uv** is installed:

```
pip install uv
```

3. Install dependencies:

```
uv sync
```

4. Open and run the notebook:

```
1.0_RAG_PDF.ipynb
```

---

### Learnings from errors generated

* Text chunking and document processing run locally and do not require API access.
* Embedding generation uses Google’s Generative AI API and is subject to free-tier rate limits.
* Large documents should be embedded in small batches to avoid quota exhaustion.

---

### Project Status

The vector store persist directory is defined in the current code structure.
Full persistence of embeddings and expansion to multi-PDF ingestion are planned in a future update.

Development is temporarily paused at the embedding stage due to Google free-tier API rate limits.
Once quota resets or billing is enabled, persistent vector storage and multi-document ingestion will be finalized in this repository.

---

### Purpose

This project is intended as a practical reference for building Retrieval-Augmented Generation pipelines using modern LLM and vector database tooling.

---