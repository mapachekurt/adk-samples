FROM python:3.11-slim
RUN pip install mcp httpx
COPY firebase_docs_mcp.py .
CMD ["python", "-m", "mcp", "run", "firebase_docs_mcp.py", "--transport", "sse"]