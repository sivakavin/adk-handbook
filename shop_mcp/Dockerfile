
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY . .

RUN uv pip install --system "mcp>=1.0.0,<2.0.0" python-dotenv

ENV PORT=8080

EXPOSE 8080

CMD ["python", "shop_server.py"]
