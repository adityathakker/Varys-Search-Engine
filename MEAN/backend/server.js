//Initialisers
var express = require("express");
var app = express();
var bodyParser = require("body-parser");
var mongoose = require("mongoose");
var database;
var KnownUrl = require('./models/KnownUrlModel.js');
var databaseName = "varys";

//Config
app.use(bodyParser.json());
app.use(function(request, response, next){
	response.header("Access-Control-Allow-Origin", "*");
	response.header("Access-Control-Allow-Headers", "Content-Type, Authorization");
	next();
});

//Connect To Database
mongoose.connect("mongodb://localhost:27017/" + databaseName, function(err, db){
	if(!err){
		console.log("Connected To MondoDB");
		database = db;
	}else{
		console.log("Error!!!!");
	}
});

//Routes
app.post("/api/search", function(request, response){
	console.log(request.body);
	var message = new Message(request.body);
	message.save();
	response.status(200);
});

app.get('/api/search', function(request, response){
	var queryToSearch = request.query.queryString;
	var words = queryToSearch.split(" ");
	var arrayLength = words.length;
	var regexReadyWords = new Array();
	for (var i = 0; i < arrayLength; i++) {
	    regexReadyWords.push(new RegExp(words[i], 'i'));
	}

	console.log(regexReadyWords);

	var arrayOfWords = new Array();

	for (var i = 0; i < arrayLength; i++) {
	    var temp = {
	    	"content.title": regexReadyWords[i]
	    };
	    arrayOfWords.push(temp);
	}
	console.log(arrayOfWords);

	KnownUrl.find({
			$and: [
				{
					status: 'indexed'
				},
				{
					"content.hints": {
						$in: regexReadyWords
					}
				},
				{
					$or: arrayOfWords
				}
			]
		}, 
		function(err, result){
			if(err){
				response.status(404);
			}else{
				if(result.length > 0){
					response.status(200);
					response.send(result);
				}else{
					response.status(200);
					response.send([{content: {title: "No Result Found :("}}]);
				}
			}
		}
	).sort({
		score: -1,
	}).select({ url: 1, score: 1, "content.title": 1, "content.infobox": 1});
});


//Functions
function getMessages(){
	KnownUrl.findOne().exec(function(err, result){
		console.log(result);
	});
}


//Server Start
var server = app.listen(5000, function(){
	console.log("Server Running On Port 5000...");
});