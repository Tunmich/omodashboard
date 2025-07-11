FROM python:3.10

WORKDIR /app
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Default command: run scheduler
CMD ["python", "scheduler/job_runner.py"]