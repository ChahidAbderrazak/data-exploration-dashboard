// pipeline {
//     // agent any

//     agent {
//         // docker {
//         //     image 'python:3.8' 
//         //     args '-v ${PWD}/logs:/app/logs -v ${PWD}/artifacts:/app/artifacts -w /app'
//         //     reuseNode true
//         // }

//         dockerfile { filename 'Dockerfile' }
//     }
//     // triggers {
//     //     pollSCM '* * * * *'
//     // }

//     stages {

//         // stage('Unit Test') {
//         //     steps {
//         //         script {
//         //             try {
//         //                 echo 'Testing..'
//         //                 sh '''
//         //                 python -m pip install --upgrade pip
//         //                 pip install pytest 
//         //                 #------------------------------------------------------------------------
//         //                 echo "Testing the code..."
//         //                 mkdir -p logs/reports/
//         //                 python -m pytest -vvrxXs --junitxml logs/reports/pytest_results.xml ./
//         //                 '''
//         //             }
//         //             catch (Exception exc) {
//         //                 currentBuild.result = 'FAILURE'
//         //                 error('Stopping early!')
//         //             }
//         //         }
//         //     }
//         //     post {
//         //         success {
//         //             junit 'logs/**/*.xml'
//         //         }
//         //     }
//         // }
//         stage('Linting') {
//             steps {
//                 script {
//                     try {
//                         sh '''
//                         python -m pip install --upgrade pip
//                         pip install flake8 black black[jupyter]
//                         #------------------------------------------------------------------------
//                         bash ./bash/0-debug.sh
//                         '''
//                     }
//                     catch (Exception exc) {
//                         currentBuild.result = 'FAILURE'
//                         error('Stopping early!')
//                     }
//                 }
//             }
            
//         }
//         stage('Data Exploration') {
//             steps {
//                 echo 'Data Exploration....'
//                 sh '''
//                 echo "Start pipeline.."
//                 python src/data_exploration.py
//                 ls
//                 pwd
//                 '''
//             }
//         }
//         // stage('Confirm to deploy the model to staging') {
//         //     steps {
//         //         timeout(time: 60, unit: 'SECONDS') {
//         //             input(message: 'Okay to Deploy?', ok: 'Let\'s Do it!')
//         //         }
//         //     }
//         // }
//         stage('Deploy API server') {
//             steps {
//                 echo 'Ruuning the API server....'
//                 sh '''
//                 echo "waiting to serve the model"
//                 '''
//             }
//         }

//         stage('Deliver') {
//             steps {
//                 echo 'model production....'
//                 sh '''
//                 echo "waintg for production"

//                 '''
//             }
//         }
//     }

//     post {
//         success {
//             echo 'build succeeded'
//         }
//         failure {
//             echo 'Build failed'
//         }
//     }
// }
