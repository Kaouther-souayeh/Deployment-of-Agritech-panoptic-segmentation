pipeline {
    pipeline {
    agent {
        docker {
            image 'python:3.7'
            args '-u root:sudo'
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
}