$(window).on("resize", function() {
  if ($("#mobile-menu-icon").is(":hidden")) {
    $("nav").show();
  } else {
		$("nav").hide();
	}
});

$(document).ready(function() {
  $('#mobile-menu-icon').on('click', function() {
  	$("nav").slideToggle();
  });
});

function formatNumber(number) {
  return number.toLocaleString("en");
}
