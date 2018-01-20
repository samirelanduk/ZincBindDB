
function drawNgl(pdb, zinc, residues, otherZincs, otherSites) {
  var stage = new NGL.Stage("ngl-site", {backgroundColor: "white"});
  stage.loadFile("rcsb://" + pdb).then(function (component) {
    // Make the whole thing a cartoon
    component.addRepresentation("cartoon", {color: "#4A9586"});

    // Select the zinc atom and make it a ball
    var zincCommand = {
        sele: zinc,
        aspectRatio: 8
    };
    component.addRepresentation("ball+stick", zincCommand);

    // Select the residues and make them sticks
    residueCommand = {
        sele: residues,
    }
    component.addRepresentation("licorice", residueCommand);

    // Make any other zincs present but transparent
    otherZincs.forEach(function(zinc) {
      zincCommand = {
        sele: zinc,
        aspectRatio: 8,
        opacity: 0.3
      };
      component.addRepresentation("ball+stick", zincCommand);
    })
    otherSites.forEach(function(site) {
      zincCommand = {
        sele: site,
        opacity: 0.3
      };
      component.addRepresentation("licorice", zincCommand);
    })

    //Centre the view on the sites
    component.autoView(residueCommand.sele);
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
