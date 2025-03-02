pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "your-dockerhub-username/fastapi-service:${BUILD_NUMBER}"
        KUBECONFIG = credentials('huawei-cce-kubeconfig')
    }

    stages {
        stage('Clone Repository') {
            steps {
                git 'https://github.com/your-username/fastapi-service.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate && pip install -r requirements.txt'
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh '. venv/bin/activate && pytest'
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                sh 'docker build -t $DOCKER_IMAGE .'
                withDockerRegistry([credentialsId: 'docker-hub-credentials', url: '']) {
                    sh 'docker push $DOCKER_IMAGE'
                }
            }
        }

        stage('Deploy PostgreSQL & FastAPI to CCE') {
            steps {
                sh '''
                kubectl --kubeconfig=$KUBECONFIG apply -f k8s/postgres-deployment.yaml
                kubectl --kubeconfig=$KUBECONFIG apply -f k8s/k8s-deployment.yaml
                kubectl --kubeconfig=$KUBECONFIG apply -f k8s/k8s-service.yaml
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh 'kubectl --kubeconfig=$KUBECONFIG get pods -n default'
                sh 'kubectl --kubeconfig=$KUBECONFIG get svc -n default'
            }
        }
    }

    post {
        success {
            echo '✅ Deployment to CCE successful!'
        }
        failure {
            echo '❌ Deployment failed!'
        }
    }
}
