pipeline {
  agent any
  stages {
    stage('setup') {
      parallel {
        stage('setup') {
          agent {
            docker {
              image 'python:latest'
            }

          }
          steps {
            echo 'Setup'
          }
        }

        stage('error') {
          steps {
            echo 'test 2'
          }
        }

      }
    }

  }
}