## PDF-Based Retrieval-Augmented Generation (RAG)

This project implements a Retrieval-Augmented Generation (RAG) pipeline that enables context-aware question answering over PDF documents using semantic search and large language models.

---

### Project Overview

The system loads a PDF file, splits its content into manageable text chunks, generates semantic embeddings using Google Gemini embedding models, stores vectors in a Chroma vector database, and performs similarity search to retrieve relevant context. Retrieved context is then passed to a Gemini chat model to produce grounded responses.

This repository serves as a reference implementation for building document-based RAG systems.

---

### Project Structure
1.0_RAG_PDF.ipynb # Main RAG pipeline notebook
Festo_File_Overview.pdf # Sample PDF used for ingestion
Vectorstore/ # Local Chroma vector database
pyproject.toml # Project dependencies (uv)
uv.lock # Locked dependency versions
.env.example # Example environment variable file

---

### Tech Stack

- Python
- LangChain
- Google Gemini Embeddings (`models/gemini-embedding-001`)
- Google Gemini Chat Model (`gemini-2.5-flash-lite`)
- Chroma Vector Database
- PyPDF Document Loader
- uv (Python package manager)

---

### How to Run

1. Add your Google API key to a `.env` file:
GOOGLE_API_KEY=your_api_key_here
pip install uv


2. Ensure **uv** is installed:
pip install uv

3. Install dependencies:
uv sync


4. Open and run the notebook:
1.0_RAG_PDF.ipynb

---

### Example Query

Sample run against `Festo_File_Overview.pdf`:

**Q:** What is main.cpp?

**A:** Based on the provided context, **main.cpp** is the **entry point of the backend program** for the Festo workstation control system. It is described as running an **infinite loop every 0.1 seconds** to perform tasks such as **reading sensors**.

---

### Project Status

**v1 (Completed):**
- ✅ Single-PDF ingestion and text extraction
- ✅ Recursive text chunking with overlap
- ✅ Gemini embedding generation
- ✅ Chroma vector store setup with persistence
- ✅ Similarity-based semantic retrieval
- ✅ Context-aware question answering with Gemini chat model

**v2 (Planned):**
- ⬜ Persistent multi-PDF ingestion
- ⬜ Batched embedding to handle large documents under API rate limits

---

### Notes & Limitations

- Text chunking and document processing run locally and do not require API access.
- Embedding generation uses Google's Generative AI API and is subject to free-tier rate limits.
- Large documents should be embedded in small batches to avoid quota exhaustion.

---

### Purpose

This project is a practical reference for building Retrieval-Augmented Generation pipelines using modern LLM and vector database tooling.