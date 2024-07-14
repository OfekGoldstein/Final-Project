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
        DOCKER_IMAGE_MAIN = 'ofekgoldstein/final-project:latest'
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
        
        stage('Create merge request') {
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
                            curl -X POST -u ${USERNAME}:${PASSWORD} \
                            -d '{ "title": "${pullRequestTitle}", "body": "${pullRequestBody}", "head": "${branchName}", "base": "main" }' \
                            ${GITHUB_API_URL}/repos/${GITHUB_REPO}/pulls
                        """
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
                        sh "docker build -t $DOCKERHUB_USERNAME/final-project:${newVersion} -f App/Dockerfile ./App"
                        
                        // Update DOCKER_IMAGE_MAIN environment variable with the new version
                        env.DOCKER_IMAGE_MAIN = "$DOCKERHUB_USERNAME/final-project:${newVersion}"
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
                            docker push $DOCKER_IMAGE_MAIN
                            """
                        }
                    }
                }
            }
        }
    }
    
post {
    always {
        script {
            // Commit the updated VERSION file back to the repository
            def branch = env.BRANCH_NAME ?: env.GIT_BRANCH.split('/')[1]  // Adjusted to handle both Multibranch and GitSCM
            def version = readFile('VERSION').trim()
            sh """
            git config --global user.email "ofekgold16@gmail.com"
            git config --global user.name "OfekGoldstein"
            git checkout ${branch}
            git add VERSION
            git commit -m "Increment version to ${version}"
            git push origin ${branch}
            """
        }
        echo "Post-build actions completed."
    }
}