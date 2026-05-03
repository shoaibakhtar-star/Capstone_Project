pipeline {
    agent any

    environment {
        AWS_REGION     = "ap-south-1"
        AWS_ACCOUNT_ID = "639914974908"
        ECR_REGISTRY   = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        APP_SERVER_ID  = "i-09db336236d870b20"
        S3_BUCKET      = "myapp-frontend-capstone"
        SECRET_ID      = "myapp/production/env"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Checking out source code..."
                checkout scm
            }
        }

        stage('Set Image Tag') {
            steps {
                script {
                    env.GIT_COMMIT_SHORT = sh(
                        script: "git rev-parse --short HEAD",
                        returnStdout: true
                    ).trim()
                    env.IMAGE_TAG = "${env.BUILD_NUMBER}-${env.GIT_COMMIT_SHORT}"
                    echo "==========================================="
                    echo "Build Number : ${env.BUILD_NUMBER}"
                    echo "Commit Hash  : ${env.GIT_COMMIT_SHORT}"
                    echo "Image Tag    : ${env.IMAGE_TAG}"
                    echo "==========================================="
                }
            }
        }

        stage('ECR Login') {
            steps {
                echo "Logging into Amazon ECR..."
                sh '''
                    aws ecr get-login-password --region $AWS_REGION | \
                    docker login --username AWS --password-stdin $ECR_REGISTRY
                '''
            }
        }

        stage('Build Docker Images') {
            parallel {
                stage('Build FastAPI') {
                    steps {
                        sh '''
                            echo "Building FastAPI image: $IMAGE_TAG"
                            docker build \
                                -t $ECR_REGISTRY/fastapi-repo:$IMAGE_TAG \
                                -t $ECR_REGISTRY/fastapi-repo:latest \
                                ./backend/python-fastapi
                        '''
                    }
                }
                stage('Build Django') {
                    steps {
                        sh '''
                            echo "Building Django image: $IMAGE_TAG"
                            docker build \
                                -t $ECR_REGISTRY/django-repo:$IMAGE_TAG \
                                -t $ECR_REGISTRY/django-repo:latest \
                                ./backend/python-django
                        '''
                    }
                }
                stage('Build Node') {
                    steps {
                        sh '''
                            echo "Building Node image: $IMAGE_TAG"
                            docker build \
                                -t $ECR_REGISTRY/node-repo:$IMAGE_TAG \
                                -t $ECR_REGISTRY/node-repo:latest \
                                ./backend/backend-node
                        '''
                    }
                }
                stage('Build .NET') {
                    steps {
                        sh '''
                            echo "Building .NET image: $IMAGE_TAG"
                            docker build \
                                -t $ECR_REGISTRY/dotnet-repo:$IMAGE_TAG \
                                -t $ECR_REGISTRY/dotnet-repo:latest \
                                ./backend/backend-dotnet
                        '''
                    }
                }
            }
        }

        stage('Push Docker Images') {
            parallel {
                stage('Push FastAPI') {
                    steps {
                        sh '''
                            docker push $ECR_REGISTRY/fastapi-repo:$IMAGE_TAG
                            docker push $ECR_REGISTRY/fastapi-repo:latest
                        '''
                    }
                }
                stage('Push Django') {
                    steps {
                        sh '''
                            docker push $ECR_REGISTRY/django-repo:$IMAGE_TAG
                            docker push $ECR_REGISTRY/django-repo:latest
                        '''
                    }
                }
                stage('Push Node') {
                    steps {
                        sh '''
                            docker push $ECR_REGISTRY/node-repo:$IMAGE_TAG
                            docker push $ECR_REGISTRY/node-repo:latest
                        '''
                    }
                }
                stage('Push .NET') {
                    steps {
                        sh '''
                            docker push $ECR_REGISTRY/dotnet-repo:$IMAGE_TAG
                            docker push $ECR_REGISTRY/dotnet-repo:latest
                        '''
                    }
                }
            }
        }

        stage('Build & Deploy Frontend to S3') {
            steps {
                dir('frontend') {
                    sh '''
                        echo "Node version: $(node --version)"
                        echo "NPM version: $(npm --version)"

                        echo "Building React frontend..."
                        npm ci
                        npm run build

                        echo "Uploading to S3 bucket: $S3_BUCKET"
                        if [ -d "dist" ]; then
                            aws s3 sync dist/ s3://$S3_BUCKET/ --delete --region $AWS_REGION
                        elif [ -d "build" ]; then
                            aws s3 sync build/ s3://$S3_BUCKET/ --delete --region $AWS_REGION
                        else
                            echo "ERROR: No build output directory found!"
                            exit 1
                        fi

                        echo "Frontend successfully deployed to s3://$S3_BUCKET"
                    '''
                }
            }
        }

        stage('Fetch Secrets & Write .env on App Server') {
            steps {
                echo "Fetching secrets from AWS Secrets Manager on app server..."
                sh """
                    aws ssm send-command \
                        --region ${AWS_REGION} \
                        --instance-ids ${APP_SERVER_ID} \
                        --document-name "AWS-RunShellScript" \
                        --comment "Fetch secrets for build #${BUILD_NUMBER}" \
                        --parameters '{"commands":["bash /app/fetch-secrets.sh"]}' \
                        --output text
                """
            }
        }

        stage('Deploy to App Server via SSM') {
            steps {
                echo "Deploying build #${env.BUILD_NUMBER} to private EC2 via SSM..."
                sh """
                    aws ssm send-command \
                        --region ${AWS_REGION} \
                        --instance-ids ${APP_SERVER_ID} \
                        --document-name "AWS-RunShellScript" \
                        --comment "Deploy build #${BUILD_NUMBER} tag ${IMAGE_TAG}" \
                        --parameters '{"commands":[
                            "echo === Starting deployment for tag ${IMAGE_TAG} ===",
                            "cd /app",
                            "echo === Logging into ECR ===",
                            "aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 639914974908.dkr.ecr.ap-south-1.amazonaws.com",
                            "echo === Stopping app containers only monitoring stays up ===",
                            "docker compose -f cloud-compose.yaml down --remove-orphans || true",
                            "echo === Removing old images to force fresh pull ===",
                            "docker image prune -af || true",
                            "echo === Pulling fresh images from ECR ===",
                            "export IMAGE_TAG=${IMAGE_TAG} && docker compose -f cloud-compose.yaml pull",
                            "echo === Starting app containers with new images ===",
                            "export IMAGE_TAG=${IMAGE_TAG} && docker compose -f cloud-compose.yaml up -d",
                            "echo === Deployment complete for tag ${IMAGE_TAG} ===",
                            "docker ps"
                        ]}' \
                        --output text
                """
            }
        }

    }

    post {
        success {
            echo """
            ✅ ================================
            Pipeline SUCCESS
            Build    : #${env.BUILD_NUMBER}
            Tag      : ${env.IMAGE_TAG}
            Commit   : ${env.GIT_COMMIT_SHORT}
            S3       : s3://${S3_BUCKET}
            ================================
            """
        }
        failure {
            echo """
            ❌ ================================
            Pipeline FAILED
            Build    : #${env.BUILD_NUMBER}
            Tag      : ${env.IMAGE_TAG}
            Commit   : ${env.GIT_COMMIT_SHORT}
            Check console output above
            ================================
            """
        }
        always {
            script {
                try {
                    sh 'docker image prune -f'
                    echo "Docker cleanup done"
                } catch (err) {
                    echo "Cleanup skipped: ${err}"
                }
            }
        }
    }
}
