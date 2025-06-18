FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install uv && \
    uv pip install -r requirements.txt --system
COPY app ./app
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
