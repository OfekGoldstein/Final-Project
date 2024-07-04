pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE_FEATURE = 'ofekgoldstein/final-project:feature-${BRANCH_NAME}'
        DOCKER_IMAGE_MAIN = 'ofekgoldstein/final-project:latest'
        
        GITHUB_PAT = 'SEPIO1wHQKTvLknxYIgVcE3ThduDaT0rPise' // GitHub PAT credential ID (configured in Jenkins credentials)
        DOCKERHUB_PAT = 'HxTiSCxTaCEznCZZWbevb7Zy3MM' // Docker Hub PAT credential ID (configured in Jenkins credentials)
        DOCKERHUB_USERNAME = 'ofekgoldstein'
    }
    
    stages {
        stage('Connect to GitHub API') {
            agent any // Use any agent for simple curl commands
            
            steps {
                script {
                    // Verify connectivity to GitHub API
                    sh "curl -s -o /dev/null -w '%{http_code}' -H 'Authorization: token ${GITHUB_PAT}' https://api.github.com"
                }
            }
        }

        stage('Checkout') {
            agent any // Use any agent for git checkout
            
            steps {
                // Check out the repository
                checkout scm
            }
        }

        stage('Feature Branch Build') {
            agent {
                docker { 
                    image 'docker:19.03'
                    reuseNode true // Reuse the same agent node for efficiency
                }
            }
            
            when {
                branch 'feature'
            }
            steps {
                script {
                    dir('App') {
                        // Build Docker image for feature branch
                        sh "docker build -t $DOCKER_IMAGE_FEATURE ."
                    }
                }
            }
        }
        
        stage('Feature Branch Test') {
            agent any // Use any agent for testing
            
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
            agent any // Use any agent for GitHub API calls
            
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
            agent {
                docker { 
                    image 'docker:19.03'
                    reuseNode true // Reuse the same agent node for efficiency
                }
            }
            
            when {
                expression {
                    // Execute only when the merge request is approved and merged
                    return currentBuild.changeSets.collect { it.branch }.flatten().contains('refs/heads/main')
                }
            }
            steps {
                script {
                    dir('App') {
                        // Build Docker image for main branch
                        sh "docker build -t $DOCKER_IMAGE_MAIN ."
                    }
                }
            }
        }
        
        stage('Main Branch Test') {
            agent any // Use any agent for testing
            
            when {
                expression {
                    // Execute only when the merge request is approved and merged
                    return currentBuild.changeSets.collect { it.branch }.flatten().contains('refs/heads/main')
                }
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
            agent {
                docker { 
                    image 'docker:19.03'
                    reuseNode true // Reuse the same agent node for efficiency
                }
            }
            
            when {
                expression {
                    // Execute only when the merge request is approved and merged
                    return currentBuild.changeSets.collect { it.branch }.flatten().contains('refs/heads/main')
                }
            }
            steps {
                script {
                    // Push Docker image to Docker Hub
                    pushToDockerHub()
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
        """, returnStdout: true)
            
        // Extract the pull request number from the GitHub API response
        def prNumber = readJSON text: response.trim().replaceAll('^[^\\d]*', '')['number']
            
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
            """, returnStdout: true)
                
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
        withCredentials([string(credentialsId: 'HxTiSCxTaCEznCZZWbevb7Zy3MM', variable: 'DOCKERHUB_PAT')]) {
            sh "echo $DOCKERHUB_PAT | docker login --username $DOCKERHUB_USERNAME --password-stdin"
            sh "docker push $DOCKER_IMAGE_MAIN"
        }
    }
}