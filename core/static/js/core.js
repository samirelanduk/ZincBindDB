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
    // Takes a species name in CAPS and title cases it in the appropriate way.

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

function addTerm(button) {
    // Adds a search term to the advanced search page. It will also add removal
    // buttons to each search term already present.

    var rows = $(button).parent().find(".search-term");
    lastRow = rows.last();
    newRow = lastRow.clone();
    newRow.find("input").val("");
    $(newRow).insertAfter(lastRow);
    rows = $(button).parent().find(".search-term");
    rows.each(function(index, row) {
        if ($(row).find("button").length == 0) {
            $(row).append('<button type="button" style="border: 0; background:\
            transparent" class="delete-button" onclick="removeRow(this)">\
            <img src="/static/images/cross.png" width="20" height="20"></button>')
        }
    });
    updateSearchTerm($(newRow).find("select"));
}

function removeRow(button) {
    var parent = $(button).parent().parent();
    var rows = parent.find(".search-term");
    $(button).parent().remove();
    rows = parent.find(".search-term");
    if (rows.length == 1) {
        rows.first().find("button").remove();
    }
}

function updateSearchTerm(select) {
    var input = $(select).parent().find("input");
    input.attr("name", $(select).val());
    var selectedOption = $(select).find(":selected").attr("data-placeholder");
    input.attr("placeholder", selectedOption);
    if ($(select).val().includes("deposited")) {
        input.attr("type", "date");
    } else {
        input.attr("type", "text");
    }
}

function validateSearch() {
    var rows = $(".search-term");
    var dataCount = 0;
    rows.each(function(index, row) {
        if ($(row).find("input").val() != "") {
            dataCount++;
        }
    });
    if (dataCount == 0) {
        $(".error-message").text("Please enter a search term");
        return false;
    } else {
        rows.each(function(index, row) {
        if ($(row).find("input").val() == "") {
            $(row).find("input").removeAttr("name");
        }
        });
        return true;
    };
}

function resortResults(select) {
    var selectedOption = $(select).find(":selected").val();
    var url = window.location.href;
    if (!(url.includes("?"))) {
        url += "?";
    }
    if (url.includes("sort=")) {
        url = url.replace(/sort=[\-a-z]+/, "sort=" + selectedOption)
    } else {
        url += "&sort=" + selectedOption;
    }
    window.location.href = url;
}
