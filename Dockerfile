FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8050

# gunicorn serves the underlying Flask server (app.server) instead of the
# Dash dev server -- more stable for anything actually deployed.
CMD ["gunicorn", "-b", "0.0.0.0:8050", "app:server"]
