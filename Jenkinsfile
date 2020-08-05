pipeline {
  stage('Initialize'){
        def dockerHome = tool 'myDocker'
        env.PATH = "${dockerHome}/bin:${env.PATH}"
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
