# DLCA Platform Prototype

This repository contains the source code of the DLCA platform prototype, including:

- `dlca-frontend/` – React + Vite frontend
- `dlca-backend/` – Flask backend

## Required Environment

Please install the following software before running the project:

- **Python 3**
- **Node.js and npm**
- **Neo4j**
- **Ollama**

The local LLM model used in this project is:

- `llama3.1:8b`

If needed, install it with:

```bash
ollama pull llama3.1:8b
```

## How to Start the System

Please start the system in the following order.

### 1. Start Neo4j

Make sure the local Neo4j database is running.

Typical local connection:
- `bolt://localhost:7687`

### 2. Start Ollama

Open a terminal and run:

```bash
ollama serve
```

### 3. Start the backend

Open another terminal and run:

```bash
cd dlca-backend
pip install -r requirements.txt
python app.py
```

The backend will usually run at:
- `http://127.0.0.1:5001`

### 4. Start the frontend

Open another terminal and run:

```bash
cd dlca-frontend
npm install
npm run dev
```

The frontend will usually run at:
- `http://localhost:5173`

### 5. Open the platform

Open the frontend address in your browser:

- `http://localhost:5173`

## Notes

- The `node_modules` folder is not included in this repository. Please run `npm install` before starting the frontend.
- Some backend runtime folders such as `results/` may be created automatically during execution.
- This project was developed and tested in a local environment.