# 📝 FastAPI Notes with pgvector & Gemini

A FastAPI application that stores and queries note embeddings using **Postgres + pgvector** and uses **free Gemini model**.  
Provides endpoints to retrieve and summarize the **top k most relevant notes** for a query.  

### ⚡ Features
- 🗂 Semantic note storage with **pgvector**  
- 🔍 Query and rank notes by similarity  
- 🧠 Summarize top results using **Gemini API**  
- 💻 Built with **FastAPI**, **SQLAlchemy**, and **Pydantic**  

### 🛠 Requirements
- [Docker](https://www.docker.com/)  
- [uv](https://docs.astral.sh/uv/) for Python package & environment management  

### 🔑 Environment
Create a `.env` file in the project root:  
```bash
POSTGRES_USER=""
POSTGRES_PASSWORD=""
POSTGRES_DB=""
GEMINI_API_KEY=""

### 🚀 Quickstart
Build & start the services:
```bash
docker compose up --build
```
Access the API:
FastAPI docs: `http://localhost:8000/docs`
