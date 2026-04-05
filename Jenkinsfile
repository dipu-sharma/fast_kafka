pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "myrepo/fastapi-app"
        SONAR_PROJECT_KEY = "fastapi-kafka"
        // Replace with actual credential IDs
        DOCKER_CREDS = 'dockerhub-credentials'
        SONAR_TOKEN = 'sonar-token'
        GITHUB_CREDS = 'github-credentials'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Dependencies & Pytest') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    # Run tests with coverage and junit report
                    pytest --junitxml=reports/junit.xml --cov=. --cov-report=xml:coverage.xml
                '''
            }
        }
        
        stage('OWASP Dependency Check') {
            steps {
                dependencyCheck additionalArguments: '--scan ./ --format XML', odcInstallation: 'Default'
                dependencyCheckPublisher pattern: 'dependency-check-report.xml'
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') { // Match this with Jenkins SonarQube Server configuration name
                    sh '''
                        # Assumes sonar-scanner is installed on the agent
                        sonar-scanner \
                          -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                          -Dsonar.sources=. \
                          -Dsonar.exclusions=venv/**,alembic/**,**/*.pyc \
                          -Dsonar.python.coverage.reportPaths=coverage.xml
                    '''
                }
            }
        }
        
        stage('Quality Gate') {
            steps {
                timeout(time: 1, unit: 'HOURS') {
                    // Wait for SonarQube webhook callback
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh "docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} ."
            }
        }
        
        stage('Trivy Image Scan') {
            steps {
                // Fail the build only on CRITICAL and HIGH vulnerabilities
                sh "trivy image --exit-code 1 --severity CRITICAL,HIGH ${DOCKER_IMAGE}:${BUILD_NUMBER}"
            }
        }
        
        stage('Docker Push') {
            steps {
                withCredentials([usernamePassword(credentialsId: env.DOCKER_CREDS, passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                    sh '''
                        echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
                        docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                    '''
                }
            }
        }
        
        stage('Update K8s Manifest (ArgoCD)') {
            steps {
                withCredentials([usernamePassword(credentialsId: env.GITHUB_CREDS, passwordVariable: 'GIT_PASSWORD', usernameVariable: 'GIT_USERNAME')]) {
                    sh """
                        # Update the image tag in deployment.yaml
                        sed -i "s|image: ${DOCKER_IMAGE}:.*|image: ${DOCKER_IMAGE}:${BUILD_NUMBER}|g" k8s/deployment.yaml
                        
                        git config user.email "jenkins@example.com"
                        git config user.name "Jenkins CI"
                        git add k8s/deployment.yaml
                        
                        # Only commit if there are changes
                        git diff --staged --quiet || git commit -m "chore: Update image tag to ${BUILD_NUMBER}"
                        
                        # Set remote URL with credentials and push
                        git remote set-url origin https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/your-org/fastapi-kafka.git
                        git push origin HEAD:main
                    """
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}
