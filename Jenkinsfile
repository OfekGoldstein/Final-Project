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
        PYTHONPATH = "${WORKSPACE}/App"
        GITHUB_API_URL = 'https://api.github.com'
        GITHUB_REPO = 'OfekGoldstein/Final-Project'
        DOCKERHUB_USERNAME = 'ofekgoldstein'
        DOCKER_IMAGE_MAIN = 'ofekgoldstein/final-project'
    }
    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: 'https://github.com/OfekGoldstein/final-project.git'
            }
        }
        
        stage('Main Branch Build') {
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
                        
                        // Update DOCKER_IMAGE environment variable with the new version
                        env.DOCKER_IMAGE = dockerImage
                        
                        // Pass newVersion to the next stage
                        currentBuild.description = newVersion
                    }
                }
            }
        }
        
        stage('Git Operations') {
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
                            
                            // Push to origin with credentials
                            sh """
                            git push https://${USERNAME}:${PASSWORD}@github.com/${GITHUB_REPO}.git main
                            """
                        }
                    }
                }
            }
        }
        
        stage('Push to Docker Hub') {
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