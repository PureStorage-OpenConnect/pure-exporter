FROM python:3-alpine

# Application directory
WORKDIR /app
COPY . /app

# Install dependencies and WSGI server
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Run as non-root user
RUN addgroup -S app && adduser -S -G app app
USER app

# Configure the image properties
# gunicorn settings: bind any, 2 threads, log to
# stdout/stderr (docker/k8s handles logs), anonymize request URL
# end of log shows request time in seconds and size in bytes
ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0:9491 \
    --workers=2 \
    --access-logfile=- \
    --error-logfile=- \
    --access-logformat=\"%(t)s %(h)s %(U)s %(l)s %(T)s %(B)s\""
EXPOSE 9491
ENTRYPOINT ["gunicorn", "pure_exporter:app"]
