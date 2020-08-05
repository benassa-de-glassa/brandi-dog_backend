pipeline {
  agent any
  stages {
    stage('setup') {
      parallel {
        stage('setup') {
          steps {
            echo 'test'
          }
        }

        stage('') {
          steps {
            echo 'test 2'
          }
        }

      }
    }

  }
}