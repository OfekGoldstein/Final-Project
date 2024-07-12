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
        DOCKER_HUB_CREDENTIALS = 'HxTiSCxTaCEznCZZWbevb7Zy3MM' // Correct Docker Hub credentials ID
        DOCKER_IMAGE_MAIN = 'ofekgoldstein/final-project:latest'
        GITHUB_PAT = 'bgLOPhFt0hgc8zfWnTfjj9h2VP2c0K3TVcna' // Ensure this is your actual GitHub PAT credential ID
        DOCKERHUB_USERNAME = 'ofekgoldstein'
        PYTHONPATH = "${WORKSPACE}/App"
        GIT_USER = "OfekGoldstein"
        GIT_PASSWORD = "Ofek1167"
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
        
        stage("Create Merge Request") {
            when {
                expression {
                    return !env.BRANCH_NAME.equals('main')
                }
            }
            steps {
                container('curl') {
                    script {
                        def BranchName = env.BRANCH_NAME
                        def mainBranch = "main"
                        def PullRequestTitle = "Merge ${BranchName} into ${mainBranch}"
                        def PullRequestBody = "Automatically generated pull request to merge ${BranchName} into ${mainBranch}"

                        sh """
                          curl -u ${GIT_USER}:${GIT_PASSWORD} -X POST -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/OfekGoldstein/Final-Project/pulls -d '{
                            "title": "${PullRequestTitle}",
                            "body": "${PullRequestBody}",
                            "head": "${BranchName}",
                            "base": "${mainBranch}"
                          }'
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
                        withCredentials([string(credentialsId: 'DOCKER_HUB_CREDENTIALS', variable: 'DOCKER_HUB_PASSWORD')]) {
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