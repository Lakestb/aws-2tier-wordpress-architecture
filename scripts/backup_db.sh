#!/bin/bash

# Thong tin cau hinh
DB_HOST="wordpress-db.cnwgwiseq95o.ap-southeast-1.rds.amazonaws.com"
DB_USER="admin"
DB_PASS="YOUR_RDS_PASSWORD_HERE"
DB_NAME="wordpress"
S3_BUCKET="my-portfolio-blog-media-635176221447-ap-southeast-1-an"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR="/tmp"
FILE_NAME="db_backup_${DATE}.sql.gz"

# Tien hanh dump va nen du lieu
mysqldump -h $DB_HOST -u $DB_USER -p$DB_PASS --set-gtid-purged=OFF --single-transaction $DB_NAME | gzip > "${BACKUP_DIR}/${FILE_NAME}"

# Day file len S3 thong qua IAM Role (khong can nhap key)
aws s3 cp "${BACKUP_DIR}/${FILE_NAME}" "s3://${S3_BUCKET}/backups/${FILE_NAME}"

# Don dep file tam tren EC2 de tiet kiem dung luong
rm -f "${BACKUP_DIR}/${FILE_NAME}"

echo "Backup complete: ${FILE_NAME} pushed to s3://${S3_BUCKET}/backups/"
