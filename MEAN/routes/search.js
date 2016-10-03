var express = require('express');
var router = express.Router();

var KnownUrl = require('../models/KnownUrl.js');

/* GET /search listing. */
router.get('/', function (req, res, next) {
    KnownUrl.find(function (err, results) {
        if (err){
            console.log("Error Occurred");
            return next(err);
        }else{
            console.log("No Error Occurred");
            res.json(results);
        }
    });
});

/* GET /todos/id */
router.get('/:id', function (req, res, next) {
    console.log("Param: " + req.params.id);
    KnownUrl.findById(req.params.id, function (err, post) {
        if (err) return next(err);
        res.json(post);
    });
});


module.exports = router;
