pipeline {
    agent any

    environment {
        AWS_REGION     = "ap-south-1"
        AWS_ACCOUNT_ID = "688939571878"
        ECR_REGISTRY   = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

        APP_SERVER_ID  = "i-088695533fe29c1b3"
        APP_SERVER_IP  = "10.0.3.151"
        SSH_USER       = "ubuntu"

        S3_BUCKET      = "myapp-frontend-688939571878"
        SECRET_ID      = "myapp/production/env"
    }

    stages {

        stage('Checkout') {
            steps {
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

                    echo "Build: ${env.BUILD_NUMBER}"
                    echo "Tag  : ${env.IMAGE_TAG}"
                }
            }
        }

        stage('ECR Login') {
            steps {
                sh '''
                    aws ecr get-login-password --region $AWS_REGION | \
                    docker login --username AWS --password-stdin $ECR_REGISTRY
                '''
            }
        }

        stage('Build Docker Images') {
            parallel {
                stage('FastAPI') {
                    steps {
                        sh '''
                            docker build -t $ECR_REGISTRY/fastapi-repo:$IMAGE_TAG \
                                         -t $ECR_REGISTRY/fastapi-repo:latest \
                                         ./backend/python-fastapi
                        '''
                    }
                }
                stage('Django') {
                    steps {
                        sh '''
                            docker build -t $ECR_REGISTRY/django-repo:$IMAGE_TAG \
                                         -t $ECR_REGISTRY/django-repo:latest \
                                         ./backend/python-django
                        '''
                    }
                }
                stage('Node') {
                    steps {
                        sh '''
                            docker build -t $ECR_REGISTRY/node-repo:$IMAGE_TAG \
                                         -t $ECR_REGISTRY/node-repo:latest \
                                         ./backend/backend-node
                        '''
                    }
                }
                stage('.NET') {
                    steps {
                        sh '''
                            docker build -t $ECR_REGISTRY/dotnet-repo:$IMAGE_TAG \
                                         -t $ECR_REGISTRY/dotnet-repo:latest \
                                         ./backend/backend-dotnet
                        '''
                    }
                }
            }
        }

        stage('Push Docker Images') {
            parallel {
                stage('FastAPI') {
                    steps {
                        sh 'docker push $ECR_REGISTRY/fastapi-repo:$IMAGE_TAG && docker push $ECR_REGISTRY/fastapi-repo:latest'
                    }
                }
                stage('Django') {
                    steps {
                        sh 'docker push $ECR_REGISTRY/django-repo:$IMAGE_TAG && docker push $ECR_REGISTRY/django-repo:latest'
                    }
                }
                stage('Node') {
                    steps {
                        sh 'docker push $ECR_REGISTRY/node-repo:$IMAGE_TAG && docker push $ECR_REGISTRY/node-repo:latest'
                    }
                }
                stage('.NET') {
                    steps {
                        sh 'docker push $ECR_REGISTRY/dotnet-repo:$IMAGE_TAG && docker push $ECR_REGISTRY/dotnet-repo:latest'
                    }
                }
            }
        }

        stage('Copy Config Files via SCP') {
            steps {
                echo "Copying config files to remote server..."

                sshagent(['ec2-key']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no $SSH_USER@$APP_SERVER_IP "mkdir -p /app"

                        scp -o StrictHostKeyChecking=no -r \
                            cloud-compose.yaml \
                            nginx.conf \
                            cloud.env \
                            monitoring \
                            scripts \
                            $SSH_USER@$APP_SERVER_IP:/app/
                    '''
                }
            }
        }

        stage('Build & Deploy Frontend to S3') {
            steps {
                dir('frontend') {
                    sh '''
                        npm ci
                        npm run build

                        if [ -d "dist" ]; then
                            aws s3 sync dist/ s3://$S3_BUCKET/ --delete --region $AWS_REGION
                        elif [ -d "build" ]; then
                            aws s3 sync build/ s3://$S3_BUCKET/ --delete --region $AWS_REGION
                        else
                            echo "No build output found"
                            exit 1
                        fi
                    '''
                }
            }
        }

        stage('Fetch Secrets via SSM') {
            steps {
                sh """
                    aws ssm send-command \
                        --region ${AWS_REGION} \
                        --instance-ids ${APP_SERVER_ID} \
                        --document-name "AWS-RunShellScript" \
                        --parameters '{"commands":["bash /app/scripts/fetch-secrets.sh"]}' \
                        --output text
                """
            }
        }

        stage('Deploy via SSM') {
            steps {
                sh """
                    aws ssm send-command \
                        --region ${AWS_REGION} \
                        --instance-ids ${APP_SERVER_ID} \
                        --document-name "AWS-RunShellScript" \
                        --parameters '{
                            "commands":[
                                "cd /app",

                                "aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}",

                                "docker image prune -af || true",

                                "export IMAGE_TAG=${IMAGE_TAG} && docker compose -f cloud-compose.yaml pull",

                                "export IMAGE_TAG=${IMAGE_TAG} && docker compose -f cloud-compose.yaml up -d --force-recreate --remove-orphans",

                                "docker ps"
                            ]
                        }' \
                        --output text
                """
            }
        }
    }

    post {
        success {
            echo "SUCCESS: Build #${env.BUILD_NUMBER} Tag ${env.IMAGE_TAG}"
        }
        failure {
            echo "FAILED: Build #${env.BUILD_NUMBER}"
        }
        always {
            sh 'docker image prune -f || true'
        }
    }
}
