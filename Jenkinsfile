pipeline {
  agent {
    docker {
      image 'python:latest'
    }

  }
  stages {
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

  }
}