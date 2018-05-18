$(window).on("resize", function() {
    // On small screens, the nav links should disappear when the page is resized
    if ($("#mobile-menu-icon").is(":visible")) {
        $("#nav-links").hide();
    }
    $("#nav-links").removeAttr("style");
});


$(document).ready(function() {
    $("#mobile-menu-icon").on("click", function() {
        var SPEED = 100;
        if ($("#nav-links").is(":hidden")) {
            $("#nav-links").slideToggle(SPEED);
        } else {
            $("#nav-links").slideToggle(SPEED, function() {
                $("#nav-links").removeAttr("style");
            });
        }
    });
});


function formatSpecies(species) {
    var words = species.toLowerCase().split(" ");
    words[0] = words[0][0].toUpperCase() + words[0].slice(1);
    var regex = /\d/g;
    for (var i = 0; i < words.length; i++) {
        if (regex.test(words[i])) {
            words[i] = words[i].toUpperCase();
        }
    }
    return words.join(" ")
}
