DevOps Project: Solar System App
Overview
This project is a web application that allows users to register, log in, and vote for their favorite planets in the solar system. It is built with Flask, MongoDB, and includes a DevOps pipeline managed using Jenkins, Docker, Kubernetes, Helm, ArgoCD, and Jira for project management.

Table of Contents:
    Features
    Technologies Used
    Setup and Installation
    Running the Application
    DevOps Pipeline
    Monitoring and Visualization
    Testing
    Project Management
    Contributing

Features:
    User authentication (registration and login)
    Voting for favorite planets
    Viewing planet data
    Dynamic UI with tooltips and styled messages

Technologies Used:
    Frontend: HTML, CSS, JavaScript
    Backend: Flask, Python
    Database: MongoDB
    DevOps: Jenkins, Docker, Kubernetes, Helm, ArgoCD, Prometheus, Grafana
    Project Management: Jira

Setup and Installation:
    Prerequisites:
        Python 3.8+
        MongoDB
        Docker
        Kubernetes
        Helm
        Jenkins
        ArgoCD
        Prometheus
        Grafana

Installation:
    Clone the repository:
        git clone https://github.com/OfekGoldstein/Final-Project.git
        cd Final-Project

    Install dependencies:
        pip install -r requirements.txt

    Set up MongoDB:
    Ensure MongoDB is running and accessible. Use the following connection string in your environment:
        MONGO_URI=mongodb://ofek:ofek2002@mongodb:27017/?authSource=Final-project

Set up Flask environment variables:
Create a .env file in the root directory with the following content:
    FLASK_APP=app.py
    FLASK_ENV=development
    SECRET_KEY=your_secret_key

Running the Application:
Start the Flask application:
    flask run

Access the application:
Open your web browser and go to http://localhost:5000.

DevOps Pipeline
Jenkins Pipeline
The Jenkins pipeline is configured to perform the following tasks:

Feature Branches:
    Import GitHub repository
    Run tests (pytest, unittest2, nose2)
    Send merge request to GitHub

Main Branch:
    Build Docker image
    Push image to Docker Hub

Kubernetes Deployment
Deploy MongoDB and the Flask application:
Use Helm to deploy MongoDB and your application:
    helm install mongodb stable/mongodb
    helm install final-project ./charts

ArgoCD:
Access ArgoCD at localhost:8081 to manage and monitor your deployments.

Monitoring and Visualization
    Prometheus
    Prometheus is used for monitoring the application. To deploy Prometheus:
        helm install prometheus stable/prometheus

    Grafana
    Grafana is used for visualizing the metrics collected by Prometheus. To deploy Grafana:
        helm install grafana stable/grafana
    After deploying Grafana, access it at http://localhost:3000 and configure it to use Prometheus as a data source.

Testing
Tests are located in the /tests directory. To run the tests, use:
    pytest
Ensure that the test configuration matches your application setup.

Project Management
This project is managed using Jira for task tracking and project planning. Key features managed in Jira include:

    User stories
    Bug tracking
    Sprint planning
    Task assignments
    Contributing
    Contributions are welcome! Please follow these steps:
        Fork the repository.
        Create a new branch (git checkout -b feature-branch).
        Commit your changes (git commit -m 'Add new feature').
        Push to the branch (git push origin feature-branch).
        Create a new Pull Request.