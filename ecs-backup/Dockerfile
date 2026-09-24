FROM debian:bookworm-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        default-mysql-client \
        gzip \
        python3-pip \
        ca-certificates && \
    pip3 install --no-cache-dir --break-system-packages awscli && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY backup_db.sh /usr/local/bin/backup_db.sh
RUN chmod +x /usr/local/bin/backup_db.sh

ENTRYPOINT ["/usr/local/bin/backup_db.sh"]
