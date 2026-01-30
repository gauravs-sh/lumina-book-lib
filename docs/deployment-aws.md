# AWS Deployment Guide

## Services
- **API**: ECS Fargate or EC2
- **Database**: RDS PostgreSQL
- **Storage**: S3 for documents if needed
- **Cache**: ElastiCache (optional)
- **CI/CD**: GitHub Actions -> ECR -> ECS

## Steps
1. Create an RDS PostgreSQL instance and update `DATABASE_URL`.
2. Build Docker image for backend (Dockerfile not included, add if required).
3. Push image to ECR.
4. Create ECS service or EC2 systemd service.
5. Configure env vars: `JWT_SECRET`, `OPENROUTER_API_KEY`, etc.
6. Deploy frontend to S3 + CloudFront or Vercel.

## Security
- Use HTTPS (ALB + ACM).
- Store secrets in AWS Secrets Manager.
- Restrict RDS access to VPC security group.

## CI/CD Example (High Level)
- `main` branch push -> build backend image -> push to ECR -> deploy ECS task.
- Frontend build -> S3 sync -> CloudFront invalidation.
