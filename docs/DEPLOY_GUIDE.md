# FabForge Deployment Guide to AWS / GCP

## AWS Deployment (ECS + EC2 or Fargate)

1. **Prerequisites**
   - AWS Account, CLI configured
   - Docker installed

2. **Build & Push**
   ```bash
   aws ecr create-repository --repository-name fabforge
   docker build -t fabforge .
   docker tag fabforge:latest <account>.dkr.ecr.us-east-1.amazonaws.com/fabforge:latest
   aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
   docker push <account>.dkr.ecr.us-east-1.amazonaws.com/fabforge:latest
   ```

3. **ECS Task Definition** (JSON with ports 8000, MQTT, etc.)

4. **Kubernetes on EKS** (use k8s/ manifests)

## GCP Deployment (GKE or Cloud Run)

1. **GKE**
   ```bash
   gcloud container clusters create fabforge-cluster
   kubectl apply -f k8s/
   ```

2. **Cloud Run** for FastAPI

Full Terraform/IaC ready in future extension.

See docker-compose.yml and k8s/ for base.
