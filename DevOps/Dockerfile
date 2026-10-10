FROM python:3.13-slim

WORKDIR /code

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY . .

EXPOSE 8000

# CMD ["uv", "run", "uvicorn", "main:app"]

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]



# docker build -t my-fastapi-app .       

# docker run -p 8000:8000 my-fastapi-app