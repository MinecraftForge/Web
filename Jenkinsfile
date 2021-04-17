pipeline {
    environment {
        GRADLE_ARGS = '-Dorg.gradle.daemon.idletimeout=5000'
    }

    stages {
        stage('build') {
            agent {
                docker {
                    image 'gradle:jdk8'
                    args '-v webgc:/home/gradle/.gradle/'
                }
            }
            steps {
                withGradle {
                    sh './gradlew ${GRADLE_ARGS} bundleFiles'
                }
            }
        }
        stage('docker') {
            agent any
            steps {
                script {
                    pagegen = docker.build("pagegen")
                    pagegen.push("latest")
                }
            }
        }
    }
}