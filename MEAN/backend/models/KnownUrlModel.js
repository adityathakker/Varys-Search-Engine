var mongoose = require('mongoose');

var KnownUrlSchema = new mongoose.Schema({
    status: String,
    url: String,
    content: {
        title: String,
        hints: [String]
    },
    score: Number,
    referral_links: [mongoose.Schema.ObjectId]
});

module.exports = mongoose.model("KnownUrl", KnownUrlSchema, "known_urls");