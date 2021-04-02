const express = require('express');
const app = express();
const mongodb = require('mongodb');
const child_process = require('child_process');

const PORT = 4000;

const MONGODB_HOST = process.env.MONGODB_HOST;
const MONGODB_PORT = process.env.MONGODB_PORT;

function testConnection() {
    var client = mongodb.MongoClient;
    client.connect('mongodb://' + MONGODB_HOST + ':' + MONGODB_PORT, function(err, db) {
        if (err) {
            console.log('Database is not connected... Waiting 1s before retry.');
            setTimeout(testConnection, 1000);
        }
        else {
            console.log('SUCCESS: Connected to Mongo Server!');
            startMongoExpressServer();
        }
    });
}

function startMongoExpressServer() {
    const appPath = '/node_modules/mongo-express/app';
    console.log('Starting Mongo Express server from ' + appPath);
    const child = child_process.exec('node ' + appPath, ['--version'], (error, stdout, stderr) => {
        if (error) {
            console.error('stderr', stderr);
            throw error;
        }
        console.log('stdout', stdout);
    });
}

app.listen(PORT, function() {
    console.log('Your node js server is running on PORT:', PORT);
    testConnection();
});
