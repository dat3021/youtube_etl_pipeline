FROM apache/airflow:3.1.8

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
RUN uv pip install -r pyproject.toml

COPY . .

ENV PYTHONPATH="/opt/airflow"