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
  - name: gh
    image: ghcr.io/github/super-linter:v4  # Using a pre-built image with GitHub CLI (gh)
    command:
    - sleep
    - infinity  # Keep the container running
    tty: true
  volumes:
  - name: docker-socket
    hostPath:
      path: /var/run/docker.sock
"""
        }
    }
    environment {
        DOCKER_HUB_CREDENTIALS = 'HxTiSCxTaCEznCZZWbevb7Zy3MM' // Correct Docker Hub credentials ID
        DOCKER_IMAGE_MAIN = 'ofekgoldstein/final-project:latest'
        GITHUB_PAT = 'bgLOPhFt0hgc8zfWnTfjj9h2VP2c0K3TVcna' // Replace with your actual GitHub PAT credential ID
        DOCKERHUB_USERNAME = 'ofekgoldstein'
        PYTHONPATH = "${WORKSPACE}/App"
    }
    stages {
        
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
                            sh 'pip install pytest mongomock -r requirements.txt'
                        }
                    }
                }
            }
        }
        
        stage('Feature Branch Test') {
            when {
                not {
                    branch 'main'
                }
                
            }
            steps {
                container('test') {
                    script {
                        dir('App') {
                            sh 'pytest tests'
                        }
                    }
                }
            }
        }
        
        stage('Create Pull Request') {
            when {
                    branch 'main'                
            }
            steps {
                container('gh') {
                script {
                    createPullRequest()
                }
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

// Function to create pull request using GitHub CLI (gh)
def createPullRequest() {
    script {
        // Ensure GitHub CLI (gh) is configured with the GitHub PAT
        sh "gh auth login --with-token <<< '${GITHUB_PAT}'"
        
        // Get the current repository URL and extract repo name
        def gitUrl = sh(script: 'git config --get remote.origin.url', returnStdout: true).trim()
        def repoName = gitUrl.replaceFirst(/^.*\/([^\/]+\/[^\/]+).git$/, '$1')
        
        echo "Creating pull request from 'feature' to 'main' for repo: ${repoName}"
        
        // Create a pull request using gh CLI (merge feature into main)
        sh "gh pr create --title 'Merge feature into main' --body 'Automated pull request from Jenkins pipeline' --base main --head feature --repo ${repoName}"
    }
}

// Function to wait for the pull request to be merged
def waitForPull(prNumber, repoName) {
    script {
        def merged = false
        while (!merged) {
            def response = sh(script: """
                curl -X GET \\
                    -H 'Authorization: token ${GITHUB_PAT}' \\
                    https://api.github.com/repos/${repoName}/pulls/${prNumber}
            """, returnStdout: true).trim()
            
            // Check if the pull request is merged
            merged = readJSON(text: response)['merged']
            
            // Wait for 30 seconds before checking again
            sleep 30
        }
        
        echo "Pull request ${prNumber} is merged. Proceeding with main branch steps."
    }
}