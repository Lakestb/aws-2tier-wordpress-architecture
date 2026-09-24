# 2-Tier Scalable WordPress Application on AWS

A production-ready, decoupled Web Architecture deployed on Amazon Web Services (AWS) adhering to the AWS Well-Architected Framework — extended beyond a basic 2-tier setup with High Availability, a Serverless module, and Containerized automation.

---

## 1. Architecture Overview

- **Compute / Presentation Tier**: Amazon EC2 (Ubuntu 24.04 LTS, Apache 2.4, PHP 8.3, WordPress 6.x), fronted by an Application Load Balancer and managed by an Auto Scaling Group for self-healing capacity.
- **Database Tier**: Amazon RDS for MySQL (decoupled from compute layer, private subnet only).
- **Object Storage**: Amazon S3 (Media offloaded via IAM Instance Profile without static credentials).
- **High Availability**: Application Load Balancer + Auto Scaling Group (Min/Desired/Max, CPU-based Target Tracking policy) across 2 Availability Zones.
- **Serverless Backend**: AWS Lambda + Amazon API Gateway + Amazon DynamoDB powering an independent Guestbook feature, decoupled from the core WordPress stack.
- **Automation & Containerization**: A Dockerized backup task running on Amazon ECS Fargate, triggered daily by Amazon EventBridge Scheduler — replacing the original EC2 cron job.
- **Monitoring & Observability**: Amazon CloudWatch Dashboard + Metric Alarm + Amazon SNS topic.
- **Auditing**: AWS CloudTrail Event History for API-level change tracking.

---

## 2. Infrastructure Specifications

| Component | AWS Service | Specification / Configuration |
| :--- | :--- | :--- |
| **Web Server** | Amazon EC2 | Ubuntu Server 24.04 LTS, `t3.micro`, launched via Launch Template |
| **High Availability** | ALB + Auto Scaling Group | Internet-facing ALB across 2 AZs; ASG Min=1, Desired=1, Max=2, Target Tracking on CPU 70% |
| **Database** | Amazon RDS | MySQL Engine, Security Group (Port 3306 restricted to app-tier SG only) |
| **Object Store**| Amazon S3 | Media offload bucket + dedicated `backups/` prefix |
| **Access Control**| AWS IAM | Least-privilege Instance Profile scoped to `s3:PutObject` / `GetObject` / `ListBucket` on the media bucket only — no static Access Keys stored on the instance |
| **Serverless API** | API Gateway + Lambda | REST API (`/guestbook`, POST, CORS enabled) → Python 3.12 function |
| **NoSQL Storage** | Amazon DynamoDB | `GuestbookMessages` table, Provisioned 5 RCU/5 WCU |
| **Container Registry** | Amazon ECR | Private repository storing the backup task image |
| **Container Runtime** | Amazon ECS Fargate | 0.25 vCPU / 0.5 GB task, environment-variable-based config (no hardcoded secrets) |
| **Scheduling** | Amazon EventBridge Scheduler | Cron `0 2 * * ? *` — daily automated backup |
| **Monitoring** | Amazon CloudWatch | Dashboard: `CPUUtilization`, `DatabaseConnections`; Alarm `>= 80%` CPU |
| **Alerting** | Amazon SNS | Email Subscription for CloudWatch Alarm |
| **Auditing** | AWS CloudTrail | Event History (90-day retention, no additional cost) |

---

## 3. Implementation Details & Proof of Work

### 3.1. Infrastructure & WordPress Deployment
WordPress successfully initialized and connected to the decoupled Amazon RDS MySQL database instance.

![WordPress Setup](images/wordpress-installed.png)

### 3.2. S3 Media Offloading via IAM Role
Media files are automatically transferred to S3 upon upload. Permissions are handled securely via a least-privilege IAM Role without storing Access Keys on the instance.

![S3 Storage](images/s3-storage.png)

### 3.3. Observability Dashboard & Alarms
CloudWatch Dashboard actively tracks compute loads and database connections in real time.

![CloudWatch Dashboard](images/cloudwatch-dashboard.png)

### 3.4. Automated Backup to S3 (Legacy Cron)
A bash script dumps the MySQL database using consistent transaction flags, compresses the output, and synchronizes with S3 storage. This was the original mechanism, later re-implemented in a containerized form (see 3.7).

```bash
# Verify backup files on S3 via AWS CLI
aws s3 ls s3://my-portfolio-blog-media-635176221447-ap-southeast-1-an/backups/
```

### 3.5. Serverless Guestbook (Lambda + API Gateway + DynamoDB)

An independent serverless feature embedded into the WordPress front-end, demonstrating decoupled event-driven design without modifying the core 2-tier stack.

```
Client (WordPress page) → API Gateway (REST, CORS enabled) → Lambda (Python 3.12) → DynamoDB
                                                                    └──→ SNS (optional email notification)
```

![Guestbook Feature](images/guestbook-feature.png)

Source code: [`lambda-guestbook/`](./lambda-guestbook)

### 3.6. High Availability (Application Load Balancer + Auto Scaling)

The EC2 web server was baked into a custom AMI and placed behind an Application Load Balancer with health-checked Target Groups. An Auto Scaling Group automatically replaces unhealthy instances and scales out under sustained CPU load.

![Auto Scaling Group Healthy Target](images/asg-healthy-target.png)

### 3.7. Containerized Backup Automation (Docker + ECS Fargate + EventBridge)

The original cron-based backup script (3.4) was containerized with Docker and re-deployed as a scheduled Amazon ECS Fargate task — fully decoupled from the EC2 instance lifecycle. Configuration (DB credentials, S3 bucket) is injected via environment variables, never hardcoded.

```bash
# Build & push to ECR
docker build -t wordpress-backup .
docker tag wordpress-backup:latest <account-id>.dkr.ecr.ap-southeast-1.amazonaws.com/wordpress-backup:latest
docker push <account-id>.dkr.ecr.ap-southeast-1.amazonaws.com/wordpress-backup:latest
```

![ECS Task Success](images/ecs-task-success.png)

Source code: [`ecs-backup/`](./ecs-backup)

---

## 4. Repository Structure

```text
aws-2tier-wordpress-architecture/
├── README.md
├── images/
│   ├── wordpress-installed.png
│   ├── s3-storage.png
│   ├── cloudwatch-dashboard.png
│   ├── backup-proof.png
│   ├── guestbook-feature.png
│   ├── asg-healthy-target.png
│   └── ecs-task-success.png
├── scripts/
│   └── backup_db.sh              # Original cron-based backup (legacy, EC2)
├── ecs-backup/
│   ├── Dockerfile
│   ├── backup_db.sh               # Containerized backup (ECS Fargate)
│   └── ecs_task_role_policy.json
├── lambda-guestbook/
│   ├── lambda_function.py
│   └── lambda_iam_policy.json
└── frontend/
    └── guestbook_form.html
```