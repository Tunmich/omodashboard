# 🔧 Use a richer base image for better networking support
FROM python:3.11-buster

# 📁 Set working directory
WORKDIR /app

# 📦 Install essential networking tools (like ping and curl)
RUN apt-get update && \
    apt-get install -y iputils-ping curl wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 📄 Copy your requirements file
COPY requirements.txt .

# 🐍 Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 🧠 Optional: Verify network connectivity
RUN curl -I https://pypi.org

# 📂 Copy project files
COPY . .

# 🏁 Set default command
CMD ["python", "your_script.py"]
