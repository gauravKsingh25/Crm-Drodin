# Simplified Dockerfile for Render
FROM frappe/erpnext:v15.0.4

# Copy CRM app
COPY . /home/frappe/frappe-bench/apps/crm

# Install CRM app
USER frappe
WORKDIR /home/frappe/frappe-bench

# Install the CRM app
RUN bench get-app crm /home/frappe/frappe-bench/apps/crm
RUN bench install-app crm

# Configure for production
USER root
EXPOSE 8000

# Start command will be handled by Render
CMD ["bench", "start"]