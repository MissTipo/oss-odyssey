FROM python:3.10-slim

# Set the working directory in the container.
WORKDIR /app

# Copy the requirements file and install dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code.
COPY . .

# Expose the port the app listens on.
EXPOSE 8000

# Set an environment variable to avoid buffering.
ENV PYTHONUNBUFFERED=1

# Copy the wait-for-it script and make it executable
COPY wait-for-it.sh /app/wait-for-it.sh
RUN chmod +x /app/wait-for-it.sh

# Run the FastAPI app with uvicorn.
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Use the entrypoint script as the startup command
ENTRYPOINT ["./entrypoint.sh"]


