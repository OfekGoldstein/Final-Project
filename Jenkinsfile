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
                container('docker') {
                    script {
                        // Install necessary dependencies and GitHub CLI (gh)
                sh 'apk update'
                sh 'apk add procps gnupg bash'
                
                // Install GitHub CLI (gh) using Alpine Linux commands
                sh 'apk add --no-cache curl'
                sh 'apk add --no-cache git'
                sh 'apk add --no-cache openssh-client'
                sh 'apk add --no-cache gh'
                    }
                }
                
                container('test') {
                    script {
                        dir('App') {
                            // Install Python dependencies
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
                            // Run tests using pytest
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
                container('docker') {
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

// Function to push Docker image to Docker Hub
def pushToDockerHub() {
    script {
        withCredentials([usernamePassword(credentialsId: DOCKER_HUB_CREDENTIALS, usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
            def dockerLogin = "docker login -u $USERNAME -p $PASSWORD"
            def dockerPush = "docker push $DOCKER_IMAGE_MAIN"
            
            // Login to Docker Hub
            sh "${dockerLogin}"
            
            // Push Docker image to Docker Hub
            sh "${dockerPush}"
        }
    }
}