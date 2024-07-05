pipeline {
    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: jnlp
    image: jenkins/inbound-agent
    resources:
      requests:
        memory: 512Mi
        cpu: 512m
  - name: docker
    image: docker:20.10.8
    command:
    - cat
    tty: true
"""
        }
    }
    environment {
        DOCKER_HUB_CREDENTIALS = 'HxTiSCxTaCEznCZZWbevb7Zy3MM'
        DOCKER_IMAGE_FEATURE = "ofekgoldstein/final-project:feature-${BRANCH_NAME}"
        DOCKER_IMAGE_MAIN = 'ofekgoldstein/final-project:latest'
        GITHUB_PAT = 'SEPIO1wHQKTvLknxYIgVcE3ThduDaT0rPise' // GitHub PAT credential ID
        DOCKERHUB_USERNAME = 'ofekgoldstein'
    }
    stages {
        stage('Check Docker Installation') {
            steps {
                container('docker') {
                    script {
                        try {
                            sh 'docker --version'
                        } catch (Exception e) {
                            error "Docker is not installed or not found in the agent's PATH."
                        }
                    }
                }
            }
        }
        stage('Connect to GitHub API') {
            steps {
                script {
                    // Verify connectivity to GitHub API
                    sh "curl -s -o /dev/null -w '%{http_code}' -H 'Authorization: token ${GITHUB_PAT}' https://api.github.com"
                }
            }
        }
        stage('Checkout') {
            steps {
                // Check out the repository
                checkout scm
            }
        }
        stage('Feature Branch Build') {
            when {
                branch 'feature'
            }
            steps {
                container('docker') {
                    script {
                        dir('App') {
                            // Build Docker image for feature branch
                            sh "docker build -t $DOCKER_IMAGE_FEATURE ."
                        }
                    }
                }
            }
        }
        stage('Feature Branch Test') {
            when {
                branch 'feature'
            }
            steps {
                script {
                    // Run tests (adjust as per your testing framework)
                    sh "pytest"
                    sh "unittest2"
                    sh "nose2"
                }
            }
        }
        stage('Create Merge Request') {
            when {
                branch 'feature'
            }
            steps {
                script {
                    createMergeRequest()
                }
            }
        }
        stage('Main Branch Build') {
            when {
                branch 'main'
            }
            steps {
                container('docker') {
                    script {
                        dir('App') {
                            // Build Docker image for main branch
                            sh "docker build -t $DOCKER_IMAGE_MAIN ."
                        }
                    }
                }
            }
        }
        stage('Main Branch Test') {
            when {
                branch 'main'
            }
            steps {
                script {
                    // Run tests (adjust as per your testing framework)
                    sh "pytest"
                    sh "unittest2"
                    sh "nose2"
                }
            }
        }
        stage('Push to Docker Hub') {
            when {
                branch 'main'
            }
            steps {
                container('docker') {
                    script {
                        // Push Docker image to Docker Hub
                        pushToDockerHub()
                    }
                }
            }
        }
    }
    post {
        success {
            // Actions to perform on pipeline success
            echo "Pipeline completed successfully."
        }
        failure {
            // Actions to perform on pipeline failure
            echo "Pipeline failed."
        }
    }
}

// Function to create merge request
def createMergeRequest() {
    script {
        def gitUrl = sh(script: 'git config --get remote.origin.url', returnStdout: true).trim()
                    
        // Create merge request using GitHub API
        def response = sh(script: """
            curl -X POST \\
                -H 'Authorization: token ${GITHUB_PAT}' \\
                -d '{\\"title\\":\\"Merge feature into main\\",\\"head\\":\\"${env.BRANCH_NAME}\\",\\"base\\":\\"main\\"}' \\
                https://api.github.com/repos/${gitUrl}/pulls
        """, returnStdout: true).trim()
            
        // Extract the pull request number from the GitHub API response
        def prNumber = readJSON(text: response)['number']
            
        // Wait for the pull request to be approved and merged
        waitForMerge(prNumber)
    }
}

// Function to wait for the pull request to be merged
def waitForMerge(prNumber) {
    script {
        def gitUrl = sh(script: 'git config --get remote.origin.url', returnStdout: true).trim()
            
        // Poll GitHub API to check if the pull request is merged
        def merged = false
        while (!merged) {
            def response = sh(script: """
                curl -X GET \\
                    -H 'Authorization: token ${GITHUB_PAT}' \\
                    https://api.github.com/repos/${gitUrl}/pulls/${prNumber}
            """, returnStdout: true).trim()
                
            // Check if the pull request is merged
            merged = readJSON(text: response)['merged']
                
            // Wait for 30 seconds before checking again
            sleep 30
        }
            
        echo "Pull request ${prNumber} is merged. Proceeding with main branch steps."
    }
}

// Function to push Docker image to Docker Hub
def pushToDockerHub() {
    script {
        withCredentials([string(credentialsId: 'dockerhub-pat', variable: 'DOCKERHUB_PAT')]) {
            sh "echo $DOCKERHUB_PAT | docker login --username $DOCKERHUB_USERNAME --password-stdin"
            sh "docker push $DOCKER_IMAGE_MAIN"
        }
    }
}