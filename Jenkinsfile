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
        def repoName = gitUrl.replaceFirst(/^.*\/([^\/]+\/[^\/]+).git$/, '$1')
        
        echo "Creating pull request from 'main' to 'feature' for repo: ${repoName}"
        
        // Perform a GET request to GitHub API (Example)
        def response = sh(script: """
            curl --request GET \\
                --url "https://api.github.com/octocat" \\
                --header "Authorization: token ${GITHUB_PAT}"
        """, returnStdout: true).trim()
        
        echo "GitHub API response:"
        echo response
        
        // Create pull request using GitHub API
        def prResponse = sh(script: """
            curl -X POST \\
                -H 'Authorization: token ${GITHUB_PAT}' \\
                -d '{\\"title\\":\\"Pull main into feature\\",\\"head\\":\\"main\\",\\"base\\":\\"feature\\"}' \\
                https://api.github.com/repos/${repoName}/pulls
        """, returnStdout: true).trim()
        
        echo "Pull request creation response:"
        echo prResponse
        
        // Check for errors
        if (prResponse.contains("Bad credentials")) {
            error "Failed to create pull request. Bad credentials."
        }
        
        // Extract the pull request number from the GitHub API response
        def prNumber = readJSON(text: prResponse)['number']
        
        if (prNumber == null) {
            error "Failed to create pull request. Response: ${prResponse}"
        }
        
        echo "Pull request number: ${prNumber}"
        
        // Wait for the pull request to be approved and merged
        waitForPull(prNumber, repoName)
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