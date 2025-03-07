pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "swr.${HUAWEI_REGION}.myhuaweicloud.com/cce/fastapi-service"
        HUAWEI_ACCESS_KEY = credentials('HUAWEI_ACCESS_KEY')
        HUAWEI_SECRET_KEY = credentials('HUAWEI_SECRET_KEY')
        HUAWEI_REGION = 'tr-west-1'
        KUBE_CONFIG = credentials('HUAWEI_KUBE_CONFIG')
        KUBE_CLUSTER_NAME = 'cce-test'
        DOCKER_USER = credentials('DOCKER_USER')
        DOCKER_PW = credentials('DOCKER_PW')
        SONAR_TOKEN = credentials('SONAR_TOKEN')
        MAJOR_VERSION = "1"
        MINOR_VERSION = "0"
        PATCH_VERSION = "0"
        BUILD_VERSION = "${BUILD_NUMBER}"
        IMAGE_VERSION = "${MAJOR_VERSION}.${MINOR_VERSION}.${PATCH_VERSION}-${BUILD_VERSION}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Set up Python') {
            steps {
                sh """
                    python -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    pip install pytest pytest-asyncio pytest-cov coverage
                """
            }
        }

        stage('Security Scan - Trivy') {
            steps {
                script {
                    // Install Trivy
                    sh """
                        sudo curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin v0.18.3
                    """
                    
                    // Security scan with Trivy
                    sh """
                        trivy fs --severity HIGH,CRITICAL .
                        trivy fs --severity HIGH,CRITICAL --format json --output trivy-report.json .
                    """
                    
                    // Archive results
                    archiveArtifacts artifacts: 'trivy-report.json', fingerprint: true
                }
            }
        }

        stage('Security Scan - Snyk') {
            steps {
                script {
                    snyk(
                        command: 'test',
                        tokenCredentialId: 'SNYK_TOKEN',
                        failOnIssues: false,
                        severity: 'high',
                        monitor: true
                    )
                }
            }
        }

        stage('Code Quality - SonarQube') {
            steps {
                script {
                    // Install SonarQube Scanner
                    sh """
                        wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.8.0.2856-linux.zip
                        unzip sonar-scanner-cli-4.8.0.2856-linux.zip
                        mv sonar-scanner-4.8.0.2856-linux ${WORKSPACE}/sonar-scanner
                    """
                    
                    // SonarQube analysis
                    sh """
                        ${WORKSPACE}/sonar-scanner/bin/sonar-scanner \\
                            -Dsonar.projectKey=fastapi-service \\
                            -Dsonar.sources=. \\
                            -Dsonar.host.url=http://localhost:9000 \\
                            -Dsonar.login=${SONAR_TOKEN} \\
                            -Dsonar.python.coverage.reportPaths=coverage.xml \\
                            -Dsonar.python.version=3.9
                    """
                }
            }
        }

        stage('Build and Push Docker Image') {
            steps {
                script {
                    // Login to Huawei SWR
                    sh """
                        docker login -u ${DOCKER_USER} -p ${DOCKER_PW} swr.${HUAWEI_REGION}.myhuaweicloud.com
                    """
                    
                    // Build and tag image with versioning
                    sh """
                        docker build -t ${DOCKER_IMAGE}:${IMAGE_VERSION} .
                        docker tag ${DOCKER_IMAGE}:${IMAGE_VERSION} ${DOCKER_IMAGE}:${MAJOR_VERSION}.${MINOR_VERSION}.${PATCH_VERSION}
                        docker tag ${DOCKER_IMAGE}:${IMAGE_VERSION} ${DOCKER_IMAGE}:${MAJOR_VERSION}.${MINOR_VERSION}
                        docker tag ${DOCKER_IMAGE}:${IMAGE_VERSION} ${DOCKER_IMAGE}:${MAJOR_VERSION}
                        docker tag ${DOCKER_IMAGE}:${IMAGE_VERSION} ${DOCKER_IMAGE}:latest
                    """
                    
                    // Security scan of Docker image with Trivy
                    sh """
                        trivy image --severity HIGH,CRITICAL ${DOCKER_IMAGE}:${IMAGE_VERSION}
                        trivy image --severity HIGH,CRITICAL --format json --output trivy-image-report.json ${DOCKER_IMAGE}:${IMAGE_VERSION}
                    """
                    
                    // Push to SWR with all tags
                    sh """
                        docker push ${DOCKER_IMAGE}:${IMAGE_VERSION}
                        docker push ${DOCKER_IMAGE}:${MAJOR_VERSION}.${MINOR_VERSION}.${PATCH_VERSION}
                        docker push ${DOCKER_IMAGE}:${MAJOR_VERSION}.${MINOR_VERSION}
                        docker push ${DOCKER_IMAGE}:${MAJOR_VERSION}
                        docker push ${DOCKER_IMAGE}:latest
                    """
                }
            }
        }

        stage('Deploy to Huawei CCE') {
            steps {
                script {
                    // Configure kubectl with CCE cluster
                    sh """
                        echo "${KUBE_CONFIG}" > kubeconfig.yaml
                        export KUBECONFIG=kubeconfig.yaml
                    """
                    
                    // Update image version in deployment.yaml
                    sh """
                        sed -i 's|image: .*|image: ${DOCKER_IMAGE}:${IMAGE_VERSION}|' k8s/deployment.yaml
                    """
                    
                    // Apply Kubernetes manifests
                    sh """
                        # Apply secrets first
                        kubectl apply -f k8s/secrets.yaml
                        
                        # Apply deployment and wait for rollout
                        kubectl apply -f k8s/deployment.yaml
                        kubectl rollout status deployment/fastapi-deployment
                        
                        # Apply other resources
                        kubectl apply -f k8s/service.yaml
                        kubectl apply -f k8s/postgres.yaml
                    """
                }
            }
        }
    }

    post {
        always {
            // Archive reports
            archiveArtifacts artifacts: 'htmlcov/**/*,trivy-report.json,trivy-image-report.json', fingerprint: true
            cleanWs()
        }
        success {
            echo "Pipeline completed successfully!"
        }
        failure {
            echo "Pipeline failed!"
        }
        unstable {
            echo "Pipeline completed with warnings (low code coverage or security issues)"
        }
    }
}
