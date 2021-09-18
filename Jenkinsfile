@Library('forge-shared-library')_

pipeline {
    agent none
    environment {
        GRADLE_ARGS = '-Dorg.gradle.daemon.idletimeout=5000'
        DISCORD_WEBHOOK = credentials('forge-discord-jenkins-webhook')
        DISCORD_PREFIX = "Job: Forge Web: ${BRANCH_NAME} Build: #${BUILD_NUMBER}"
        JENKINS_HEAD = 'https://wiki.jenkins-ci.org/download/attachments/2916393/headshot.png'
    }

    stages {
        stage('notify_start') {
            when {
                not {
                    changeRequest()
                }
            }
            steps {
                discordSend(
                    title: "${DISCORD_PREFIX} Started",
                    successful: true,
                    result: 'ABORTED', //White border
                    thumbnail: JENKINS_HEAD,
                    webhookURL: DISCORD_WEBHOOK
                )
            }
        }
        stage('build') {
            when {
                not {
                    changeRequest()
                }
            }
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
        stage('build_test') {
            when {
                changeRequest()
            }
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
            when {
                not {
                    changeRequest()
                }
            }
            steps {
                script {
                    docker.build("pagegen")
                }
            }
        }
    }
    post {
        always {
            script {
                if (env.CHANGE_ID == null) { // This is unset for non-PRs
                    discordSend(
                        title: "${DISCORD_PREFIX} Finished ${currentBuild.currentResult}",
                        description: '```\n' + getChanges(currentBuild) + '\n```',
                        successful: currentBuild.resultIsBetterOrEqualTo("SUCCESS"),
                        result: currentBuild.currentResult,
                        thumbnail: JENKINS_HEAD,
                        webhookURL: DISCORD_WEBHOOK
                    )
                }
            }
        }
    }
}
