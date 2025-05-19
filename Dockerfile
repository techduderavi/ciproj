FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create data directory and set permissions
RUN mkdir -p /app/data && chmod 777 /app/data

ENV PORT=5000
ENV DEPLOYMENT_ENV=blue

EXPOSE 5000

# Initialize the database during container startup
CMD ["sh", "-c", "python init_db.py && python app.py"]
