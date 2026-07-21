FROM python:3.12-slim

RUN pip install --no-cache-dir \
    fastapi==0.114.2 \
    uvicorn[standard] \
    sqlalchemy[asyncio] \
    aiosqlite \
    httpx \
    pydantic[email]

WORKDIR /app
COPY src/ ./src/
ENV PYTHONPATH=/app/src
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
