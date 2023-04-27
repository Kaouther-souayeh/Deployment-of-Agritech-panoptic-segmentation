pipeline {
    agent any
    tools{
        docker {
            image 'python:3.9-slim-buster'
        }
    }
    stages {
        stage('Install dependencies') {
            steps {
                sh 'pip install -Ur requirements.txt'
            }
        }
        stage('Run tests') {
            steps {
                sh 'pip install pytest'
                sh 'pytest test_Data_preparation.py'
            }
        }
    }
}