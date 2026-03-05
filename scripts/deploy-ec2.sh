#!/usr/bin/env bash
set -euo pipefail

#######################################################################
# StakeholderSim — Automated EC2 Deployment Script
#
# Prerequisites:
#   - AWS CLI configured (aws configure) with appropriate permissions
#   - SSH key pair (will create one if needed)
#   - .env file in project root with ANTHROPIC_API_KEY
#
# Usage:
#   ./scripts/deploy-ec2.sh
#
# Environment variables (optional overrides):
#   AWS_REGION          - AWS region (default: us-east-1)
#   INSTANCE_TYPE       - EC2 instance type (default: t2.medium)
#   KEY_NAME            - SSH key pair name (default: stakeholdersim-key)
#   POSTGRES_PASSWORD   - DB password (default: auto-generated)
#   SECRET_KEY          - JWT secret (default: auto-generated)
#######################################################################

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
AWS_REGION="${AWS_REGION:-us-east-1}"
INSTANCE_TYPE="${INSTANCE_TYPE:-t2.medium}"
KEY_NAME="${KEY_NAME:-stakeholdersim-key}"
SG_NAME="stakeholdersim-sg"
KEY_FILE="$PROJECT_DIR/$KEY_NAME.pem"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 24)}"
SECRET_KEY="${SECRET_KEY:-$(openssl rand -base64 48 | tr -dc 'a-zA-Z0-9' | head -c 48)}"

echo "============================================"
echo "  StakeholderSim EC2 Deployment"
echo "============================================"
echo "Region:        $AWS_REGION"
echo "Instance type: $INSTANCE_TYPE"
echo "Key pair:      $KEY_NAME"
echo ""

# ------------------------------------------------------------------
# Step 1: Look up latest Amazon Linux 2023 AMI
# ------------------------------------------------------------------
echo "[1/6] Looking up latest Amazon Linux 2023 AMI..."
AMI_ID=$(aws ec2 describe-images \
  --region "$AWS_REGION" \
  --owners amazon \
  --filters "Name=name,Values=al2023-ami-2023*-x86_64" "Name=state,Values=available" \
  --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
  --output text)

if [ -z "$AMI_ID" ] || [ "$AMI_ID" = "None" ]; then
  echo "ERROR: Could not find Amazon Linux 2023 AMI in $AWS_REGION"
  exit 1
fi
echo "  AMI: $AMI_ID"

# ------------------------------------------------------------------
# Step 2: Create or reuse SSH key pair
# ------------------------------------------------------------------
echo "[2/6] Setting up SSH key pair..."
if aws ec2 describe-key-pairs --key-names "$KEY_NAME" --region "$AWS_REGION" &>/dev/null; then
  echo "  Key pair '$KEY_NAME' already exists"
  if [ ! -f "$KEY_FILE" ]; then
    echo "  WARNING: Key file $KEY_FILE not found locally."
    echo "  If you lost the .pem file, delete the key pair in AWS and re-run."
    exit 1
  fi
else
  echo "  Creating new key pair '$KEY_NAME'..."
  aws ec2 create-key-pair \
    --key-name "$KEY_NAME" \
    --region "$AWS_REGION" \
    --query 'KeyMaterial' \
    --output text > "$KEY_FILE"
  chmod 400 "$KEY_FILE"
  echo "  Saved to $KEY_FILE"
fi

# ------------------------------------------------------------------
# Step 3: Create or reuse security group
# ------------------------------------------------------------------
echo "[3/6] Setting up security group..."
SG_ID=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=$SG_NAME" \
  --region "$AWS_REGION" \
  --query 'SecurityGroups[0].GroupId' \
  --output text 2>/dev/null || echo "None")

if [ "$SG_ID" = "None" ] || [ -z "$SG_ID" ]; then
  SG_ID=$(aws ec2 create-security-group \
    --group-name "$SG_NAME" \
    --description "StakeholderSim - SSH, API, Frontend" \
    --region "$AWS_REGION" \
    --query 'GroupId' \
    --output text)

  # SSH
  aws ec2 authorize-security-group-ingress \
    --group-id "$SG_ID" --region "$AWS_REGION" \
    --protocol tcp --port 22 --cidr 0.0.0.0/0

  # Backend API
  aws ec2 authorize-security-group-ingress \
    --group-id "$SG_ID" --region "$AWS_REGION" \
    --protocol tcp --port 8000 --cidr 0.0.0.0/0

  # Frontend
  aws ec2 authorize-security-group-ingress \
    --group-id "$SG_ID" --region "$AWS_REGION" \
    --protocol tcp --port 3002 --cidr 0.0.0.0/0

  echo "  Created security group: $SG_ID"
else
  echo "  Reusing security group: $SG_ID"
fi

# ------------------------------------------------------------------
# Step 4: Launch EC2 instance
# ------------------------------------------------------------------
echo "[4/6] Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
  --image-id "$AMI_ID" \
  --instance-type "$INSTANCE_TYPE" \
  --key-name "$KEY_NAME" \
  --security-group-ids "$SG_ID" \
  --block-device-mappings '[{"DeviceName":"/dev/xvda","Ebs":{"VolumeSize":20,"VolumeType":"gp3"}}]' \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=StakeholderSim}]" \
  --region "$AWS_REGION" \
  --query 'Instances[0].InstanceId' \
  --output text)

echo "  Instance ID: $INSTANCE_ID"
echo "  Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids "$INSTANCE_ID" --region "$AWS_REGION"

EC2_PUBLIC_IP=$(aws ec2 describe-instances \
  --instance-ids "$INSTANCE_ID" \
  --region "$AWS_REGION" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo "  Public IP: $EC2_PUBLIC_IP"

# Wait for SSH to become available
echo "  Waiting for SSH to become available..."
for i in $(seq 1 30); do
  if ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no -o ConnectTimeout=5 ec2-user@"$EC2_PUBLIC_IP" "echo ok" &>/dev/null; then
    break
  fi
  sleep 5
done

# ------------------------------------------------------------------
# Step 5: Install Docker on EC2
# ------------------------------------------------------------------
echo "[5/6] Installing Docker on EC2..."
ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no ec2-user@"$EC2_PUBLIC_IP" << 'REMOTE_SCRIPT'
set -euo pipefail

# Install Docker
sudo yum update -y -q
sudo yum install -y -q docker

# Install Docker Compose plugin
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -sL "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

echo "Docker $(docker --version) installed"
echo "Docker Compose $(docker compose version) installed"
REMOTE_SCRIPT

# ------------------------------------------------------------------
# Step 6: Copy project and start services
# ------------------------------------------------------------------
echo "[6/6] Deploying application..."

# Create production .env on the EC2 instance
# First, read the ANTHROPIC_API_KEY from local .env
if [ -f "$PROJECT_DIR/.env" ]; then
  ANTHROPIC_API_KEY=$(grep -E '^ANTHROPIC_API_KEY=' "$PROJECT_DIR/.env" | cut -d'=' -f2-)
fi

if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  echo "  WARNING: ANTHROPIC_API_KEY not found in .env — conversations will fail"
fi

# rsync project files (exclude dev artifacts)
rsync -azP --delete \
  --exclude '.git' \
  --exclude 'node_modules' \
  --exclude '__pycache__' \
  --exclude '.next' \
  --exclude '*.pem' \
  --exclude '.env' \
  --exclude '.claude' \
  --exclude 'postgres_data' \
  --exclude 'redis_data' \
  -e "ssh -i $KEY_FILE -o StrictHostKeyChecking=no" \
  "$PROJECT_DIR/" ec2-user@"$EC2_PUBLIC_IP":~/stakeholdersim/

# Create production .env on EC2
ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no ec2-user@"$EC2_PUBLIC_IP" << REMOTE_ENV
cat > ~/stakeholdersim/.env << 'ENVFILE'
# Production environment
POSTGRES_USER=stakeholder_sim
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=stakeholder_sim
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
SECRET_KEY=$SECRET_KEY
EC2_PUBLIC_IP=$EC2_PUBLIC_IP
ENV=production
ENVFILE
REMOTE_ENV

# Build and start services (newgrp to pick up docker group)
ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no ec2-user@"$EC2_PUBLIC_IP" << 'REMOTE_START'
cd ~/stakeholdersim
sudo docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
REMOTE_START

echo ""
echo "============================================"
echo "  Deployment Complete!"
echo "============================================"
echo ""
echo "  Frontend:  http://$EC2_PUBLIC_IP:3002"
echo "  API:       http://$EC2_PUBLIC_IP:8000"
echo "  API Docs:  http://$EC2_PUBLIC_IP:8000/docs"
echo ""
echo "  Instance:  $INSTANCE_ID"
echo "  Region:    $AWS_REGION"
echo "  SSH:       ssh -i $KEY_FILE ec2-user@$EC2_PUBLIC_IP"
echo ""
echo "  Test login:"
echo "    Email:    student1@stakeholdersim.edu"
echo "    Password: student123"
echo ""
echo "  To tear down:"
echo "    aws ec2 terminate-instances --instance-ids $INSTANCE_ID --region $AWS_REGION"
echo ""
