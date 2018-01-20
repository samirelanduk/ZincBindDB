
function drawNgl(pdb, zinc, residues, otherZincs, otherSites) {
  var stage = new NGL.Stage("ngl-site", {backgroundColor: "white"});
  stage.loadFile("rcsb://" + pdb).then(function (component) {
    // Make the whole thing a cartoon
    component.addRepresentation("cartoon", {sele: "/0"});

    // Select the zinc atom and make it a ball
    component.addRepresentation("ball+stick", {sele: zinc, aspectRatio: 8});

    // Select the residues and make them sticks
    component.addRepresentation("licorice", {sele: residues});

    // Make any other zincs present but transparent
    otherZincs.forEach(function(zinc) {
      component.addRepresentation("ball+stick", {
          sele: zinc, aspectRatio: 8, opacity: 0.3
      });
    })
    otherSites.forEach(function(site) {
      component.addRepresentation("licorice", {sele: site, opacity: 0.3});
    })

    //Centre the view on the site
    component.autoView(residues);
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
  $("#ngl-site").width(width);
  $("#ngl-site").height(height);
  stage.handleResize();
}
