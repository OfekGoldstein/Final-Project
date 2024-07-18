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
              - name: argocd
                image: argoproj/argocd:v2.1.1
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
        ARGOCD_SERVER_URL = 'localhost:8081'
    }

    stages {
        stage('Clone Repository') {
            when {
                not {
                    branch 'main'
                }
            }
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
                            // Install necessary dependencies
                            sh 'apt-get update && apt-get install -y procps'
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
                        sh "docker build -t ${env.dockerImage} -f App/Dockerfile ./App"
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
                container('git') {
                    withCredentials([usernamePassword(credentialsId: 'github-creds', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                        script{
                            git branch: 'main', url: 'https://github.com/OfekGoldstein/Final-Project.git'
                            dir('final-project') {
                                sh '''
                                BUILD_NUMBER=${BUILD_NUMBER}
                                sed -i "s/tag:.*/tag: 1.0.${BUILD_NUMBER}/" values.yaml
                                echo "New tag 1.0.${BUILD_NUMBER} written to values.yaml"
                                ls -l
                                git config --global --add safe.directory /home/jenkins/agent/workspace/final-project-pipeline_main
                                git config --global user.email "ofekgold16@gmail.com"
                                git config --global user.name "OfekGoldstein"
                                git add values.yaml
                                git commit -m "Modified values.yaml"
                                git push https://${USERNAME}:${PASSWORD}@github.com/OfekGoldstein/Final-Project.git main
                                '''
                            }
                        }
                    }
                }
            }
        }

        stage('ArgoCD Sync') {
            when {
                branch 'main'
            }
            steps {
                script {
                    def WebhookURL = "http://localhost:8081/api/webhook?project=default&application=solar-system-app"
                    sh "curl -X POST '${WebhookURL}' -H 'Content-Type: application/json' -d '{}'"
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
