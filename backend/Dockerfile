FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Use the Flask development server
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
