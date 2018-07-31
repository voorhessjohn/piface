// Load the AWS SDK for Node.js
var AWS = require('aws-sdk');
// Set the region 
AWS.config.update({region: 'us-east-2'});

// Create the DynamoDB service object
ddb = new AWS.DynamoDB({apiVersion: '2012-10-08'});

var params = {
  TableName: 'piface',
  Key: {
    'ID' : {N: '4'},
  },
  ProjectionExpression: 'Emotion_1, Confidence_1'
};

// Call DynamoDB to read the item from the table
ddb.getItem(params, function(err, data) {
  if (err) {
    console.log("Error", err);
  } else {
    console.log("Success", data);
  }

var Emotion_1 = data.Item.Emotion_1.S
var Confidence_1 = data.Item.Confidence_1.N
console.log(Emotion_1,Confidence_1)

});
