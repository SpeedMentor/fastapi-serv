pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "swr.${HUAWEI_REGION}.myhuaweicloud.com/cce/fastapi-service"
        HUAWEI_ACCESS_KEY = credentials('HUAWEI_ACCESS_KEY')
        HUAWEI_SECRET_KEY = credentials('HUAWEI_SECRET_KEY')
        HUAWEI_REGION = 'tr-west-1'
        KUBE_CONFIG = credentials('KUBE_CONFIG')
        KUBE_CLUSTER_NAME = 'cce-test'
        DOCKER_USER = credentials('DOCKER_USER')
        DOCKER_PW = credentials('DOCKER_PW')
    }

    stages {
        stage('Clone Repository') {
            steps {
                git 'https://github.com/your-username/fastapi-service.git'
            }
        }

        stage('Code Quality Analysis (SonarQube)') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh 'sonar-scanner -Dsonar.projectKey=fastapi-service -Dsonar.sources=. -Dsonar.host.url=http://sonarqube:9000'
                }
            }
        }

        stage('Dependency Security Check (Snyk)') {
            steps {
                snykSecurity task: 'test'
            }
        }

        stage('Build & Test') {
            steps {
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate && pip install -r requirements.txt'
                sh '. venv/bin/activate && pytest --junitxml=test-results.xml'
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('Container Security Check (Trivy)') {
            steps {
                sh 'trivy image --exit-code 1 --severity HIGH,CRITICAL $DOCKER_IMAGE:${BUILD_NUMBER} || true'
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                script {
                    def imageTag = "${DOCKER_IMAGE}:${BUILD_NUMBER}"
                    sh "docker build -t ${imageTag} ."
                    withDockerRegistry([credentialsId: 'docker-hub-credentials', url: '']) {
                        sh "docker push ${imageTag}"
                    }
                }
            }
        }
    }

    post {
        success {
            echo "✅ Build successful! Docker Image Version: ${BUILD_NUMBER}"
        }
        failure {
            echo "❌ Build failed! Check logs for details."
        }
    }
}
