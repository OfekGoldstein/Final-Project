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
        BASE_VERSION = '0.1.0'
        MAJOR_VERSION = '0'
        MINOR_VERSION = '1'
        PATCH_VERSION = '0'
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
                        // Calculate the new version based on Jenkins build number
                        env.NEW_VERSION = "${env.MAJOR_VERSION}.${env.MINOR_VERSION}.${env.PATCH_VERSION}"
            
                        // Build Docker image with the new version
                        def dockerImage = "${DOCKER_IMAGE_MAIN}:${env.NEW_VERSION}"
                        sh "docker build -t ${dockerImage} -f App/Dockerfile ./App"
            
                        // Increment the patch version for next build
                        def newPatchVersion = env.PATCH_VERSION.toInteger() + 1
                        env.PATCH_VERSION = newPatchVersion.toString()
            
                        // Update DOCKER_IMAGE_MAIN environment variable with the new version
                        env.DOCKER_IMAGE = dockerImage

                        // Log the new version
                        echo "New version: ${env.NEW_VERSION}"
                        echo "Incremented patch version for next build: ${env.PATCH_VERSION}"
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
                            // Push Docker image to Docker Hub with the new version
                            sh """
                            echo $PASSWORD | docker login -u $USERNAME --password-stdin
                            docker push ${DOCKER_IMAGE}
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