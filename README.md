# chatalysis

Chatalysis is a small demo application that lets you explore CSV data in a chat like interface. The backend is built with **FastAPI** and uses Xinference for audio transcription and an Ollama model for generating responses. The frontend is a simple **Vue 3** app served with Vite.

## Configuration

Copy `.env.sample` to `.env` and update the values to point at your running Xinference and Ollama servers:

```bash
cp .env.sample .env
```

Available variables are:

- `XINFERENCE_URL` – base URL for the Xinference server
- `XINFERENCE_MODEL_NAME` – name of the Whisper model to launch
- `XINFERENCE_MODEL_SIZE` – size of the Whisper model
- `OLLAMA_BASE_URL` – base URL for the Ollama server
- `OLLAMA_MODEL` – model name used by LangChain

## Local development

Install dependencies with [uv](https://github.com/astral-sh/uv) and start the backend:

```bash
uv pip install -r backend/requirements.txt
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

In a separate terminal start the frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` in your browser.

## Docker

The project can also be launched using Docker. After creating your `.env` file run:

```bash
docker-compose up --build
```

The frontend will be available on `http://localhost:3000` and the API on `http://localhost:8000`.
