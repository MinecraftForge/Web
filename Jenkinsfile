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
                    args '-v webgc:/home/gradle/.gradle/ -v files_staticfiles:/out'
                }
            }
            steps {
                withGradle {
                    sh './gradlew ${GRADLE_ARGS} bundleFiles'
                }
                sh 'unzip -o build/distributions/files-bundle.zip -d /out'
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
    }
}
