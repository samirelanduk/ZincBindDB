function drawNgl(code) {
    var stage = new NGL.Stage("ngl-display", {backgroundColor: "white"});

    stage.loadFile("rcsb://" + code).then(function (component) {
        // Make the whole thing a cartoon
        component.addRepresentation("cartoon", {sele: "/0"});
    });

    // Handle resizing of the window
    stage.handleResize();
    $(window).on("resize", function() {
        handleResize();
    })
}

function handleResize() {
  var width = $("#ngl-container").width();
  var height = $("#ngl-container").height();
  $("#ngl-display").width(width);
  $("#ngl-display").height(height);
  $("canvas").width(width);
  $("canvas").height(height);
  stage.handleResize();
}
