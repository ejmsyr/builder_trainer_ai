FROM python:3.10-slim

# System packages
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    sudo \
    procps && \
    rm -rf /var/lib/apt/lists/*

# Create user
RUN useradd -m agent
WORKDIR /home/agent

# Copy code
COPY . .

# Set permissions
RUN chown -R agent:agent /home/agent
RUN chmod +x entrypoint.sh

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Switch to non-root user
USER agent

# Entrypoint
ENTRYPOINT ["./entrypoint.sh"]

