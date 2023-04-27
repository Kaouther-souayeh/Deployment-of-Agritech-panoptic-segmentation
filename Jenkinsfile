pipeline {
    agent any
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
