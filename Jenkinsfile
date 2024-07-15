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
                  requests: {}
              - name: docker
                image: docker:20.10.8
                command:
                - cat
                tty: true
                volumeMounts:
                - name: docker-socket
                  mountPath: /var/run/docker.sock
              - name: test
                image: python:3.9-slim
                command:
                - cat
                tty: true
                volumeMounts:
                - name: docker-socket
                  mountPath: /var/run/docker.sock
              - name: git
                image: alpine/git
                command:
                - cat
                tty: true
              volumes:
              - name: docker-socket
                hostPath:
                  path: /var/run/docker.sock
            """
        }
    }
    
    environment {
        DOCKER_IMAGE_MAIN = 'ofekgoldstein/final-project'
        PYTHONPATH = "${WORKSPACE}/App"
        GITHUB_API_URL = 'https://api.github.com'
        GITHUB_REPO = 'OfekGoldstein/Final-Project'
        DOCKERHUB_USERNAME = 'ofekgoldstein'
        LAST_KNOWN_STATUS = [:]
    }
    
    stages {
        stage('Scan GitHub Pull Requests') {
            triggers {
                cron('*/1 * * * *')  // Runs every minute
            }
            
            steps {
                script {
                    def pullRequests = getPullRequests()

                    for (pullRequest in pullRequests) {
                        def prNumber = pullRequest.number
                        def currentStatus = pullRequest.state
                        def lastStatus = LAST_KNOWN_STATUS[prNumber] ?: ''

                        if (currentStatus == 'merged' && lastStatus == 'open') {
                            echo "Pull Request ${prNumber} merged! Triggering main pipeline..."

                            build job: 'main-pipeline', parameters: [string(name: 'PR_NUMBER', value: "${prNumber}")]
                        }

                        LAST_KNOWN_STATUS[prNumber] = currentStatus
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
            when {
                not {
                    branch 'main'
                }
            }
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
        
        stage('Create Merge Request') {
            when {
                not {
                    branch 'main'
                }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'github-creds', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                    script {
                        def branchName = "feature"      
                        def pullRequestTitle = "Merge ${branchName} into main"
                        def pullRequestBody = "Automatically generated merge request for branch ${branchName}"

                        // Create the pull request
                        def response = sh (
                            script: """
                                curl -s -X POST -u ${USERNAME}:${PASSWORD} \
                                -d '{ "title": "${pullRequestTitle}", "body": "${pullRequestBody}", "head": "${branchName}", "base": "main" }' \
                                ${GITHUB_API_URL}/repos/${GITHUB_REPO}/pulls
                            """,
                            returnStdout: true
                        ).trim()
                        
                        // Extract pull request number from the response
                        def pullRequestNumber = readJSON text: response
                        echo "Pull request created: ${GITHUB_REPO}/pull/${pullRequestNumber.number}"
                        
                        // Record pull request number for further use
                        env.PULL_REQUEST_NUMBER = pullRequestNumber.number.toString()
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
                        // Read the current version
                        def version = readFile('VERSION').trim()
                        
                        // Increment the version
                        def (major, minor, patch) = version.tokenize('.')
                        patch = (patch.toInteger() + 1).toString()
                        def newVersion = "${major}.${minor}.${patch}"
                        
                        // Update the VERSION file with the new version
                        writeFile(file: 'VERSION', text: newVersion)
                        
                        // Build Docker image with the new version
                        def dockerImage = "${DOCKER_IMAGE_MAIN}:${newVersion}"
                        sh "docker build -t ${dockerImage} -f App/Dockerfile ./App"
                        
                        // Update DOCKER_IMAGE_MAIN environment variable with the new version
                        env.DOCKER_IMAGE = dockerImage
                        
                        // Pass newVersion to the next stage
                        currentBuild.description = newVersion
                    }
                }
            }
        }
        
        stage('Git Operations') {
            when {
                branch 'main'
            }
            steps {
                container('git') {
                    script {
                        withCredentials([usernamePassword(credentialsId: 'github-creds', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                            // Retrieve newVersion from the previous stage
                            def newVersion = currentBuild.description
                            
                            // Configure git user
                            sh "git config --global user.email 'ofekgold16@gmail.com'"
                            sh "git config --global user.name 'OfekGoldstein'"
                            
                            // Add the workspace directory to safe directories
                            sh "git config --global --add safe.directory ${WORKSPACE}"
                            
                            // Checkout the branch
                            sh "git checkout main"
                            
                            // Add VERSION file
                            sh "git add VERSION"
                            
                            // Commit the changes
                            sh "git commit -m 'Increment version to ${newVersion}'"
                            
                            // Push to origin
                            sh "git push https://${USERNAME}:${PASSWORD}@github.com/${GITHUB_REPO}.git main"
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
                        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                            sh """
                            echo $PASSWORD | docker login -u $USERNAME --password-stdin
                            docker push $DOCKER_IMAGE
                            """
                        }
                    }
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully."
        }
        failure {
            echo "Pipeline failed."
        }
    }
}

def getPullRequests() {
    def response = httpRequest(
        url: "${GITHUB_API_URL}/repos/${GITHUB_REPO}/pulls",
        authentication: 'BASIC',
        username: USERNAME,
        password: PASSWORD
    )
}
    return readJSON text: response.content