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
  - name: curl
    image: curlimages/curl:latest
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
 //       DOCKER_HUB_CREDENTIALS = withCredentials('dockerhub-token') // Correct Docker Hub credentials ID
        DOCKER_IMAGE_MAIN = 'ofekgoldstein/final-project:latest'
   //     GITHUB_PAT = 'bgLOPhFt0hgc8zfWnTfjj9h2VP2c0K3TVcna' // Ensure this is your actual GitHub PAT credential ID
        DOCKERHUB_USERNAME = 'ofekgoldstein'
        PYTHONPATH = "${WORKSPACE}/App"
        GITHUB_API_URL = 'https://api.github.com'
        GITHUB_REPO = 'OfekGoldstein/Final-Project'
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
        
        stage('Create merge request'){
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

                        sh """
                            curl -L \
                            -X POST \
                            -H "Accept: application/vnd.github+json" \
                            -H "Authorization: Bearer Ofek1167" \
                            -H "X-GitHub-Api-Version: 2022-11-28" \
                            https://api.github.com/repos/OfekGoldstein/Final-Project/pulls \
                            -d '{"title":"Amazing new feature","body":"Please pull these awesome changes in!","head":"feature","base":"main"}'
                        """
                    }
                }
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
                        withCredentials([string(credentialsId: 'dockerhub-token', variable: 'DOCKER_HUB_CREDENTIALS')]) {
                            sh "echo $DOCKER_HUB_PASSWORD | docker login -u $DOCKERHUB_USERNAME --password-stdin"
                            sh "docker push $DOCKER_IMAGE_MAIN"
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