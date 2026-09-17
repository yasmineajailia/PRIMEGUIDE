var express = require('express');
var bodyParser = require('body-parser');
var app = express();

//Allow all requests from all domains & localhost
app.all('/*', function(req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type, Accept");
  res.header("Access-Control-Allow-Methods", "POST, GET");
  next();
});

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: false}));

var ingredients = [
    {
        "id": "1",
        "text": "Eggs"
    },
    {
        "id": "2",
        "text": "Milk"
    },
    {
        "id": "3",
        "text": "Bacon"
    },
    {
        "id": "4",
        "text": "Frog Legs"
    }
];


app.get('/', function(req, res) {
    console.log("GET From SERVER");
    res.send(ingredients);
});

app.post('/', function(req, res) {
    var ingredient = req.body;
    ingredients.push(ingredient);
    res.status(200).send("Successfully posted ingredient");
});

app.listen(6060);
