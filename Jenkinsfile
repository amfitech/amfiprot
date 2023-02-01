pipeline {
  agent any

  options {
    skipDefaultCheckout(true)
  }

  stages {
    stage('Checkout') {
      steps {
        deleteDir()
        checkout scm
      }
    }
    stage('Set up venv') {
      steps {
        bat """
          python -m venv .\\venv --upgrade-deps
          call .\\venv\\Scripts\\activate.bat
          pip install -r requirements.txt
          pip install -e .
        """
      }
    }
    stage('Unit test') {
      steps {
        bat """
          call .\\venv\\Scripts\\activate.bat
          python -m unittest discover -s .\\tests
        """
      }
    }
    // stage('Lint') {
    //   steps {
    //     bat """
    //       call .\\venv\\Scripts\\activate.bat
    //       call pylint src
    //       if %errorlevel%==0 (
    //          echo Pylint finished with no warnings.
    //          exit /b 0
    //       )

    //       if %errorlevel%==4 (
    //         echo Pylint finished with warnings.
    //         exit /b 0
    //       )
    //     """
    //   }
    // }
    stage('Build docs') {
      steps {
        bat """
          call .\\venv\\Scripts\\activate.bat
          call .\\doc\\make.bat html
        """
      }
    }
  }
}

