FROM python:3.12-slim
WORKDIR /app
RUN pip install psutil requests
COPY monitor.py .
CMD ["python", "monitor.py"]
