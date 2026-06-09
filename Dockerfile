FROM python:3.11-slim

# Install system deps
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project
COPY . /app

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt pybind11 fastapi uvicorn paho-mqtt asyncua torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Build C++ core and bindings
RUN mkdir -p build && cd build && cmake .. && make -j2

# Install Python package
RUN pip install -e .

EXPOSE 8000 8501 1883

CMD ["uvicorn", "dashboard.fastapi_backend:app", "--host", "0.0.0.0", "--port", "8000"]