$(window).on("resize", function() {
  if ($("#mobile-menu-icon").is(":hidden")) {
    $("#nav-links").show();
  } else {
		$("#nav-links").hide();
	}
});

$(document).ready(function() {
  $('#mobile-menu-icon').on('click', function() {
  	$("#nav-links").slideToggle();
  });
});
