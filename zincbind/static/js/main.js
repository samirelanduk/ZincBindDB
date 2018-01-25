$(window).on("resize", function() {
  if ($("#mobile-menu-icon").is(":hidden")) {
    $("nav").show();
  } else {
    $("nav").hide();
  }
});

$(document).ready(function() {
  $('#mobile-menu-icon').on('click', function() {
  	$("nav").slideToggle("fast");
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

function checkEmpty() {
    var value = $("#term").val();
    if (value === "") {
        $(".error-message").text("Please enter a search term")
        return false;
    };
    return true;
}


function updateSearchTerm(select) {
  var input = $(select).parent().find("input");
  input.attr("name", $(select).val());
}


function addSearchRow(button) {
  var rows = $(button).parent().find(".search-row");
  lastRow = rows.last();
  newRow = lastRow.clone();
  newRow.find("input").val("");
  $(newRow).insertAfter(lastRow);
  rows = $(button).parent().find(".search-row");
  rows.each(function(index, row) {
    if ($(row).find("button").length == 0) {
      $(row).append('<button type="button" onclick="removeRow(this)">x</button>')
    }
  });
  updateSearchTerm($(newRow).find("select"));
}


function removeRow(button) {
  var rows = $(button).parent().parent().find(".search-row");
  if (rows.length == 2) {
    rows.first().find("button").remove();
  }
  $(button).parent().remove();
}


function validateSearch() {
  var rows = $(".search-row");
  var dataCount = 0;
  rows.each(function(index, row) {
    if ($(row).find("input").val() == "") {
      $(row).find("input").removeAttr("name");
    } else {
      dataCount++;
    }
  });
  if (dataCount == 0) {
      $(".error-message").text("Please enter a search term")
      return false;
  };
  return true;
}


function updateSelector(select) {
    var value = $(select).find(":selected").val();
    $("code").html(value);
}
