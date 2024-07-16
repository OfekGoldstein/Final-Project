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
        HELM_REPO_URL = 'https://github.com/OfekGoldstein/Final-Project/tree/main/final-project.git'
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'feature', url: 'https://github.com/OfekGoldstein/Final-Project.git'
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
                            sh 'apk add --no-cache procps'
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
                        env.dockerImage = "${DOCKER_IMAGE_MAIN}:1.0.${BUILD_NUMBER}"
                        sh "docker build -t ${env.dockerImage} -f App/Dockerfile ${WORKSPACE}/App"
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
                            docker push ${env.dockerImage}
                            """
                        }
                    }
                }
            }
        }

        stage('Increment Values Tag') {
            when {
                branch 'main'
            }
            steps {
                script {
                    dir('final-project') {
                        sh '''
                        sed -i 's/tag:.*/tag: 1.0.${BUILD_NUMBER}/' values.yaml
                        '''
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