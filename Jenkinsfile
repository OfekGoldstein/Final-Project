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
  - name: test
    image: python:3.9-slim
    command:
    - cat
    tty: true
    volumeMounts:
    - name: docker-socket
      mountPath: /var/run/docker.sock
  volumes:
  - name: docker-socket
    hostPath:
      path: /var/run/docker.sock
"""
        }
    }
    environment {
        DOCKER_HUB_CREDENTIALS = 'HxTiSCxTaCEznCZZWbevb7Zy3MM'
        DOCKER_IMAGE_MAIN = 'ofekgoldstein/final-project:latest'
        GITHUB_PAT = '1rXtSTvjFtOI9LPlW5nPQgUnV3qqOP1YX4CH' // Replace with your actual GitHub PAT credential ID
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
        
        stage('Clone Repository') {
            steps {
                git branch: 'feature', url: 'https://github.com/OfekGoldstein/final-project.git'
            }
        }
        
        stage('Setup Environment') {
            steps {
                container('test') {
                    script {
                        dir('App') {
                            // Install necessary dependencies
                            sh 'apt-get update'
                            sh 'apt-get install -y procps'
                            sh 'pip install --upgrade pip'
                            sh 'pip install pytest'
                            sh 'pip install mongomock'
                            sh 'pip install -r requirements.txt'
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
                container('test') {
                    script {
                        dir('App') {
                            sh 'ls -l'
                            // Run Flask app in the background
//                            sh 'python app.py &'
//                            sleep 10  // Wait for the app to start
                            
                            // Run tests
                            sh 'cd tests'
                            sh 'pytest'
                        }
                    }
                }
            }
            post {
                always {
                    // Clean up steps
                    container('test') {
                        sh 'pkill -f "python app.py"'  // Stop Flask app after tests
                    }
                }
            }
        }
        
        stage('Create pull Request') {
            when {
                branch 'feature'
            }
            steps {
                script {
                    createPullRequest()
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

// Function to create pull request
def createPullRequest() {
    script {
        def gitUrl = sh(script: 'git config --get remote.origin.url', returnStdout: true).trim()
                    
        // Create pull request using GitHub API
        def response = sh(script: """
            curl -X POST \\
                -H 'Authorization: token ${GITHUB_PAT}' \\
                -d '{\\"title\\":\\"Pull feature into main\\",\\"head\\":\\"${env.BRANCH_NAME}\\",\\"base\\":\\"main\\"}' \\
                https://api.github.com/repos/${gitUrl}/pulls
        """, returnStdout: true).trim()
            
        // Extract the pull request number from the GitHub API response
        def prNumber = readJSON(text: response)['number']
            
        // Wait for the pull request to be approved and pulled
        waitForPull(prNumber)
    }
}

// Function to wait for the pull request to be pulled
def waitForPull(prNumber) {
    script {
        def gitUrl = sh(script: 'git config --get remote.origin.url', returnStdout: true).trim()
            
        // Poll GitHub API to check if the pull request is pulled
        def pulled = false
        while (!pulled) {
            def response = sh(script: """
                curl -X GET \\
                    -H 'Authorization: token ${GITHUB_PAT}' \\
                    https://api.github.com/repos/${gitUrl}/pulls/${prNumber}
            """, returnStdout: true).trim()
                
            // Check if the pull request is pulled
            pulled = readJSON(text: response)['pulled']
                
            // Wait for 30 seconds before checking again
            sleep 30
        }
            
        echo "Pull request ${prNumber} is pulled. Proceeding with main branch steps."
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