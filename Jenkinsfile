pipeline {
    agent {
        docker {
            image 'gradle:jdk8'
            args '-v webgc:/home/gradle/.gradle/'
        }
    }
    environment {
        GRADLE_ARGS = '-Dorg.gradle.daemon.idletimeout=5000'
    }

    stages {
        stage('build') {
            steps {
                withGradle {
                    sh './gradlew ${GRADLE_ARGS} bundleFiles'
                }
                script {
                    pagegen = docker.build("pagegen")
                    pagegen.push("latest")
                }
            }
        }
    }
}