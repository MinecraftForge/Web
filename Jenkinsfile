pipeline {
    agent none
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
                    docker.build("pagegen")
                }
            }
        }
        stage('deploystaticfiles') {
            agent {
                docker {
                    image 'alpine:latest'
                    args '-v files_staticfiles:/out'
                }
            }
            steps {
                sh 'unzip build/distributions/files-bundle.zip /out/'
            }
        }
    }
}