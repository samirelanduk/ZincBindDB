function drawNgl(code, metals, residues, individual_residues, zoom) {
    // Make a stage
    stage = new NGL.Stage("ngl-container", {backgroundColor: "#ffffff"});

    // If the user double clicks, make it full screen
    stage.viewer.container.addEventListener("dblclick", function () {
        stage.toggleFullscreen();
    });

    // If the screen changes size, deal with it
    function handleResize () {
      stage.handleResize();
    }
    window.addEventListener("orientationchange", handleResize, false);
    window.addEventListener("resize", handleResize, false);

    // Load the PDB
    var load = NGL.getQuery("load");
    if (load) stage.loadFile(load, );
    stage.loadFile("rcsb://" + code + ".mmtf").then(function(component) {
        // Make the whole thing a cartoon representation
        stage.rep = component.addRepresentation("cartoon", {sele: "/0"});

        // Make metals appear as spheres
        component.addRepresentation("ball+stick", {sele: metals, aspectRatio: 8});

        // Make residue side chains appear as sticks
        component.addRepresentation("licorice", {sele: residues});

        // Add distance lines where appropriate
        for (var r = 0; r < individual_residues.length; r++) {
            var selector = individual_residues[r] + " or " + metals;
            component.addRepresentation("contact", {sele: selector});
        }

        // Store the representations
        stage.metals = metals;
        stage.residues = residues;

        // Create a holder for residue colors
        stage.residueColors = {};

        // Zoom the appropriate ammount
        if (zoom) {
            component.autoView(residues);
        } else {
            component.autoView();
        }
    });
}


function setUpControls() {
    // Make the residue labels highlight residues
    var classes = ["metal", "residue"];
    for (var i = 0; i < 2; i++) {
        var class_ = classes[i];
        $("." + class_).each(function(x) {
            $(this).click(function(e) {
                var rep = $(this).hasClass("metal") ? "ball+stick" : "licorice";
                var selector = $(this).attr("data-ngl");
                if ($(this).hasClass("active")) {
                    $(this).removeClass("active");
                    stage.residueColors[selector].setVisibility(false);
                } else {
                    $(this).addClass("active");
                    var r = stage.compList[0].addRepresentation(rep, {
                     color: "#16a085", aspectRatio: 8, sele: selector
                    });
                    stage.residueColors[selector] = r;
                }
            });
        });
    }

    // Make color picker work
    $("#colorPicker").change(function(e) {
        var color = $("#colorPicker").val();
        $("canvas").css("background-color", color);
    })

    // Make surface shower work
    var surface;
    $("#surfaceToggle").click(function(e) {
        this.classList.toggle('active');
        if ($(this).hasClass("active")) {
            surface = stage.compList[0].addRepresentation("surface", {
             sele: stage.residues, probeRadius: 0.75
            });
        } else {
            surface.setVisibility(false)
            stage.compList[0].addRepresentation(
             "licorice", {sele: stage.residues}
            );
        }
    })

    // Make spinner work
    $("#spinToggle").click(function(e) {
        this.classList.toggle('active');
        if ($(this).hasClass("active")) {
            stage.setSpin(true);
        } else {
            stage.setSpin(false);
        }
    })

    // Make backbone switcher work
    $(".backbone").change(function(e) {
        stage.rep.setVisibility(false);
        stage.rep = stage.compList[0].addRepresentation(
         this.value, {sele: "/0 and (not water)"}
        );
        stage.rep.setVisibility(true);
    })
}
