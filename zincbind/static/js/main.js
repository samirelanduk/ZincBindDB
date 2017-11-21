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

function formatNumber(number) {
  return number.toLocaleString("en");
}

function formatSpecies(species) {
	var words = species.toLowerCase().split();
	words[0] = words[0][0].toUpperCase() + words[0].slice(1);
	return words.join()
}
