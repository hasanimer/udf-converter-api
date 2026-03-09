FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/saidsurucu/UDF-Toolkit.git && \
    cd UDF-Toolkit && \
    pip install --no-cache-dir -r requirements.txt

RUN cp UDF-Toolkit/*.py /app/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

EXPOSE 10000

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "2", "--timeout", "60", "server:app"]
