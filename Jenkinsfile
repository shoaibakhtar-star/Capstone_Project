pipeline {
    agent any

    environment {
        AWS_REGION     = "ap-south-1"
        AWS_ACCOUNT_ID = "639914974908"
        ECR_REGISTRY   = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        APP_SERVER_ID  = "i-09db336236d870b20"
        S3_BUCKET      = "myapp-frontend-capstone"

        // Secrets from Jenkins credentials store
        DB_HOST        = credentials('DB_HOST')
        DB_PASSWORD    = credentials('DB_PASSWORD')
        SECRET_KEY     = credentials('SECRET_KEY')
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
                    // Tag format: buildNumber-commitHash  e.g. 42-a3f9c12
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
                        echo "Installing Node.js..."
                        curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
                        apt-get install -y nodejs

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

        stage('Write .env on App Server') {
            steps {
                echo "Writing .env file onto app server via SSM..."
                sh '''
                    aws ssm send-command \
                        --region $AWS_REGION \
                        --instance-ids $APP_SERVER_ID \
                        --document-name "AWS-RunShellScript" \
                        --comment "Write .env for build #${BUILD_NUMBER}" \
                        --parameters commands=["bash -c 'cat > /home/ubuntu/cloud.env << ENVEOF
DB_HOST=$DB_HOST
DB_PORT=3306
DB_USER=admin
DB_PASSWORD=$DB_PASSWORD
DB_NAME=userdb
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
FASTAPI_PORT=8000
PORT=8002
FRONTEND_PORT=3000
MYSQL_PORT=3306
ENVEOF
echo .env written successfully'"] \
                        --output text
                '''
            }
        }

        stage('Deploy to App Server via SSM') {
            steps {
                echo "Deploying build #${env.BUILD_NUMBER} to private EC2 via SSM..."
                sh '''
                    aws ssm send-command \
                        --region $AWS_REGION \
                        --instance-ids $APP_SERVER_ID \
                        --document-name "AWS-RunShellScript" \
                        --comment "Deploy build #${BUILD_NUMBER} tag ${IMAGE_TAG}" \
                        --parameters commands=["bash -c '
                            cd /home/ubuntu &&
                            aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 639914974908.dkr.ecr.ap-south-1.amazonaws.com &&
                            docker compose -f cloud-compose.yaml pull &&
                            docker compose -f cloud-compose.yaml up -d --remove-orphans &&
                            docker image prune -f &&
                            echo Deployment complete for tag ${IMAGE_TAG}
                        '"] \
                        --output text
                '''
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