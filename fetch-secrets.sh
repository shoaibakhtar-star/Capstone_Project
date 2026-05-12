#!/bin/bash

echo "Fetching secrets from AWS Secrets Manager..."

SECRET=$(aws secretsmanager get-secret-value \
    --secret-id myapp/production/env_new \
    --region ap-south-1 \
    --query SecretString \
    --output text)

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to fetch secrets from Secrets Manager"
    exit 1
fi

# Parse JSON and write to cloud.env
cat > /app/cloud.env <<ENVEOF
DB_HOST=$(echo $SECRET | python3 -c "import sys,json; print(json.load(sys.stdin)['DB_HOST'])")
DB_PORT=3306
DB_USER=$(echo $SECRET | python3 -c "import sys,json; print(json.load(sys.stdin)['DB_USER'])")
DB_PASSWORD=$(echo $SECRET | python3 -c "import sys,json; print(json.load(sys.stdin)['DB_PASSWORD'])")
DB_NAME=$(echo $SECRET | python3 -c "import sys,json; print(json.load(sys.stdin)['DB_NAME'])")
SECRET_KEY=$(echo $SECRET | python3 -c "import sys,json; print(json.load(sys.stdin)['SECRET_KEY'])")
ALGORITHM=HS256
FASTAPI_PORT=8000
PORT=8002
FRONTEND_PORT=3000
MYSQL_PORT=3306
ENVEOF

echo "cloud.env written successfully from Secrets Manager"
cat /app/cloud.env