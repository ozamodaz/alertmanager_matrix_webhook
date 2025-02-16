FROM python:3.9-slim

WORKDIR /app

COPY matrix_alert_webhook.py .

RUN pip install --no-cache-dir flask requests markdown2

EXPOSE 5001

CMD ["python", "matrix_alert_webhook.py"]