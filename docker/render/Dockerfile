# Multi-stage Dockerfile for Frappe CRM on Render
FROM node:18-bullseye as frontend-builder

# Build frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --only=production
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV FRAPPE_USER=frappe
ENV FRAPPE_USER_HOME=/home/$FRAPPE_USER
ENV BENCH_PATH=$FRAPPE_USER_HOME/frappe-bench

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    sudo \
    vim \
    software-properties-common \
    build-essential \
    libssl-dev \
    libffi-dev \
    libmysqlclient-dev \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libwebp-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    tcl8.6-dev \
    tk8.6-dev \
    wkhtmltopdf \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

# Install yarn
RUN npm install -g yarn

# Create frappe user
RUN useradd -ms /bin/bash $FRAPPE_USER && \
    usermod -aG sudo $FRAPPE_USER && \
    echo "$FRAPPE_USER ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER $FRAPPE_USER
WORKDIR $FRAPPE_USER_HOME

# Install bench
RUN pip install --user frappe-bench

# Add local bin to PATH
ENV PATH="$FRAPPE_USER_HOME/.local/bin:$PATH"

# Initialize bench
RUN bench init --skip-redis-config-generation --skip-assets --python $(which python3) frappe-bench

WORKDIR $BENCH_PATH

# Install Frappe
RUN bench get-app --branch version-15 frappe

# Copy CRM app
COPY --chown=$FRAPPE_USER:$FRAPPE_USER . ./apps/crm/

# Copy built frontend from previous stage
COPY --from=frontend-builder --chown=$FRAPPE_USER:$FRAPPE_USER /app/frontend/dist ./apps/crm/crm/public/frontend/

# Install CRM app
RUN bench install-app crm

# Create common_site_config.json
RUN echo '{\
 "background_workers": 1,\
 "file_watcher_port": 6787,\
 "frappe_user": "'"$FRAPPE_USER"'",\
 "gunicorn_workers": 4,\
 "live_reload": false,\
 "rebase_on_pull": false,\
 "restart_supervisor_on_update": false,\
 "restart_systemd_on_update": false,\
 "serve_default_site": true,\
 "shallow_clone": true,\
 "socketio_port": 9000,\
 "use_redis_auth": false\
}' > sites/common_site_config.json

# Create production configuration script
COPY docker/render/configure-site.sh ./configure-site.sh
RUN chmod +x ./configure-site.sh

EXPOSE 8000

# Copy startup scripts
COPY docker/render/start.sh ./start.sh
COPY docker/render/worker.sh ./worker.sh
COPY docker/render/scheduler.sh ./scheduler.sh
RUN chmod +x ./start.sh ./worker.sh ./scheduler.sh

CMD ["./start.sh"]