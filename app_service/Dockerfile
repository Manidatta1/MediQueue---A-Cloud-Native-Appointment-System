# Use official Python Image
FROM python:3.10-slim

# set wiorking directory
WORKDIR /app


# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Copy all app fils into container
COPY . .


# Expose FastAPI port
EXPOSE 8000


# Command to start the FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
