FROM python:3.11-slim

WORKDIR /app

# los archivos están dentro de 'backend', pero como el Root Directory en Render ya es 'backend',
# aquí copiamos desde la carpeta actual.
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app/app

ENV PORT=8000
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
