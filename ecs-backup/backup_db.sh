#!/bin/bash
set -euo pipefail

# Các biến môi trường bắt buộc phải truyền vào container:
#   DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, S3_BUCKET

: "${DB_HOST:?DB_HOST chưa được thiết lập}"
: "${DB_USER:?DB_USER chưa được thiết lập}"
: "${DB_PASSWORD:?DB_PASSWORD chưa được thiết lập}"
: "${DB_NAME:?DB_NAME chưa được thiết lập}"
: "${S3_BUCKET:?S3_BUCKET chưa được thiết lập}"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FILE_NAME="db_backup_${TIMESTAMP}.sql.gz"
TMP_PATH="/tmp/${FILE_NAME}"

echo "[$(date)] Bắt đầu backup database '${DB_NAME}' từ host '${DB_HOST}'"

mysqldump \
  --single-transaction \
  -h "${DB_HOST}" \
  -u "${DB_USER}" \
  -p"${DB_PASSWORD}" \
  "${DB_NAME}" | gzip > "${TMP_PATH}"

echo "[$(date)] Dump xong, kích thước file: $(du -h "${TMP_PATH}" | cut -f1)"
echo "[$(date)] Đang upload lên s3://${S3_BUCKET}/backups/${FILE_NAME}"

aws s3 cp "${TMP_PATH}" "s3://${S3_BUCKET}/backups/${FILE_NAME}"

rm -f "${TMP_PATH}"
echo "[$(date)] Hoàn tất backup: ${FILE_NAME}"