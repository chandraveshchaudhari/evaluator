# Dockerfile for Evaluator Sandbox
FROM python:3.12-slim

# Create a non-root user (for safety)
RUN useradd -m sandboxuser

# Switch to non-root
USER sandboxuser
WORKDIR /home/sandboxuser

# Copy only required packages (no evaluator logic)
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Jupyter dependencies safely
RUN pip install nbformat nbclient pandas numpy matplotlib

# Restrict network access by default (done at runtime with --network=none)
ENTRYPOINT ["python3"]
