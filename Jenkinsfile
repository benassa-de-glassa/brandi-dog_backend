pipeline {
  agent any
  stages {
    stage('init') {
      agent any
      steps {
        echo 'initializing'
        sh '''pip install pytest
; pytest'''
      }
    }

  }
}