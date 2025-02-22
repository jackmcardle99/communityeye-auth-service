# Use an official Python runtime as a parent image
FROM python:3.11

# Install PostgreSQL development libraries and Flyway
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    wget \
    libc6 \
    zlib1g \
    && wget -qO- https://repo1.maven.org/maven2/org/flywaydb/flyway-commandline/9.16.3/flyway-commandline-9.16.3-linux-x64.tar.gz | tar xvz -C /opt \
    && ln -s /opt/flyway-9.16.3/flyway /usr/local/bin/flyway \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Define environment variable
ENV FLASK_APP=app.py

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]
