## 📝 **FastAPI Notes: Semantic Search with pgvector and Google Gemini**

A FastAPI application that stores and queries note embeddings using **Postgres + pgvector** and uses **free Gemini model**.  
Provides endpoints to retrieve and summarize the **top k most relevant notes** for a query.  

### ⚡ Features
- 🗂 Semantic note storage with **pgvector**  
- 🔍 Query and rank notes by similarity  
- 🧠 Summarize top results using **Gemini API**  
- 💻 Built with **FastAPI**, **SQLAlchemy**, and **Pydantic**  
-----

### 🛠️ **Prerequisites**

  * **Docker**: For containerizing the application and its database.
  * **uv**: A high-performance Python package and environment manager from Astral.

-----

### 🔑 **Configuration**

Create a `.env` file in the project's root directory and populate it with the necessary credentials:

```bash
POSTGRES_USER="your_postgres_username"
POSTGRES_PASSWORD="your_postgres_password"
POSTGRES_DB="your_postgres_database"
GEMINI_API_KEY="your_gemini_api_key"
```

-----

### 🚀 **Getting Started**

1.  **Build and Run Services**: Start the application and its dependencies using Docker Compose.

    ```bash
    docker compose up --build -d
    ```

2.  **Access the API Documentation**: Once the services are running, the interactive API documentation can be accessed in your browser.

    ```
    http://localhost:8000/docs
    ```

3.  **Stop Services**: To stop and remove the containers, along with their volumes:

    ```bash
    docker compose down -v
    ```
