FROM python:3.11.5-alpine
LABEL maintainer="Tombo H."

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Install required dependencies, including Node.js and npm
RUN apk add --no-cache \
    git \
    gcc \
    musl-dev \
    libffi-dev \
    nodejs \
    npm

WORKDIR /src

# Clone the project from the Git repository
RUN git clone --depth 1 https://github.com/Tomixbo/DSA_Website_v1.git

WORKDIR /src/DSA_Website_v1

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Add entrypoint script
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

# Run the entrypoint
ENTRYPOINT ["/entrypoint.sh"]
