$(document).ready(function () {
    var materialColors = ["f44336", "9C27B0", "3F51B5", "03A9F4", "009688", "8BC34A", "FF9800", "FF5722", "795548", "607D8B"];
    var materialColorsDark = ["c62828", "6A1B9A", "283593", "0277BD", "00695C", "558B2F", "4CAF50", "EF6C00", "4E342E", "37474F"];
    var random = Math.floor(Math.random() * 10);
    $("body").css("background-color", "#" + materialColors[random]);
    $(".search-wrapper input:first:visible").focus();

    $("body").fadeTo("slow", 1);

});
