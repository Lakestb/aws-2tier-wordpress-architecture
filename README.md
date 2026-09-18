# 2-Tier Scalable WordPress Application on AWS

A production-ready, decoupled 2-Tier Web Architecture deployed on Amazon Web Services (AWS) adhering to the AWS Well-Architected Framework.

---

## 1. Architecture Overview
- **Compute / Presentation Tier**: Amazon EC2 (Ubuntu 24.04 LTS, Apache 2.4, PHP 8.3, WordPress 6.x).
- **Database Tier**: Amazon RDS for MySQL (Multi-AZ ready, decoupled from compute layer).
- **Object Storage**: Amazon S3 (Media offloaded via IAM Instance Profile without static credentials).
- **Monitoring & Observability**: Amazon CloudWatch Dashboard + Metric Alarm + Amazon SNS topic.
- **Disaster Recovery**: Automated database dump script, gzip compression, and S3 lifecycle synchronization via Cron.

---

## 2. Infrastructure Specifications

| Component | AWS Service | Specification / Configuration |
| :--- | :--- | :--- |
| **Web Server** | Amazon EC2 | Ubuntu Server 24.04 LTS, Security Group (Ports 80, 22) |
| **Database** | Amazon RDS | MySQL Engine, Security Group (Port 3306 restricted) |
| **Object Store**| Amazon S3 | Custom Bucket Policy for public read, Block Public Access tuned |
| **Access Control**| AWS IAM | EC2 Instance Profile (`EC2-S3-FullAccess-Role`) |
| **Monitoring** | Amazon CloudWatch | Custom Dashboard: `CPUUtilization`, `DatabaseConnections` |
| **Alerting** | Amazon SNS | Email Subscription triggered on `CPUUtilization >= 80%` |
| **Automation** | AWS CLI + Cron | Daily backup scheduled at 02:00 AM (`0 2 * * *`) |

---

## 3. Implementation Details & Proof of Work

### 3.1. Infrastructure & WordPress Deployment
WordPress successfully initialized and connected to the decoupled Amazon RDS MySQL database instance.

![WordPress Setup](images/wordpress-installed.png)

### 3.2. S3 Media Offloading via IAM Role
Media files are automatically transferred to S3 upon upload. Permissions are handled securely via IAM Roles without storing Access Keys on the instance.

![S3 Storage](images/s3-storage.png)

### 3.3. Observability Dashboard & Alarms
CloudWatch Dashboard actively tracks compute loads and database connections in real time.

![CloudWatch Dashboard](images/cloudwatch-dashboard.png)

### 3.4. Automated Backup to S3
A bash script dumps the MySQL database using consistent transaction flags, compresses the output, and synchronizes with S3 storage.

```bash
# Verify backup files on S3 via AWS CLI
aws s3 ls s3://my-portfolio-blog-media-635176221447-ap-southeast-1-an/backups/
```
## 4. Repository Structure

```text
aws-2tier-wordpress-architecture/
├── README.md
├── images/
│   ├── wordpress-installed.png
│   ├── s3-storage.png
│   ├── cloudwatch-dashboard.png
│   └── backup-proof.png
└── scripts/
    └── backup_db.sh
```
