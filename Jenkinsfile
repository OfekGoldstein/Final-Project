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
    }
    
    stages {  
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
                        def buildNumber = env.BUILD_NUMBER
            
                        // Build Docker image with the build number as part of the tag
                        def dockerImage = "${DOCKER_IMAGE_MAIN}:${buildNumber}"
                        sh "docker build -t ${dockerImage} -f App/Dockerfile ./App"
            
                        // Update DOCKER_IMAGE_MAIN environment variable with the new version
                        env.DOCKER_IMAGE = dockerImage
            
                        // Pass buildNumber to the next stage (optional)
                        currentBuild.description = buildNumber
            
                        // Debugging output (optional)
                        echo "Docker image built: ${dockerImage}"
                    }
                }
            }
        }
        
        // Add other stages as needed
        
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
                            docker push ${DOCKER_IMAGE_MAIN}:${env.BUILD_NUMBER}
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