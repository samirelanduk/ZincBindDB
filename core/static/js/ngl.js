function drawNgl(code, assembly, metals, residues, bonds, zoom) {
    // Make a stage
    stage = new NGL.Stage("ngl-container", {backgroundColor: "#ffffff"});

    // What assembly should be used?
    stage.assembly = assembly == "None" ? "AU" : "BU" + assembly;

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
        stage.rep = component.addRepresentation("cartoon", {sele: "/0", assembly: stage.assembly});

        // Make metals appear as spheres
        component.addRepresentation("ball+stick", {sele: metals, aspectRatio: 8, assembly: stage.assembly});

        // Make residue side chains appear as sticks
        if (residues.length > 0) {
            component.addRepresentation("licorice", {sele: residues, assembly: stage.assembly});
        }

        // Add distance lines where appropriate
        for (var b = 0; b < bonds.length; b++) {
            var metalPos = bonds[b][0];
            var atomPos = bonds[b][1];
            var vector = [
                metalPos[0] - atomPos[0], metalPos[1] - atomPos[1], metalPos[2] - atomPos[2]
            ]
            DIV = 16;
            miniVector = [vector[0] / DIV, vector[1] / DIV, vector[2] / DIV]
            lines = []
            for (x = 0; x <= DIV; x++) {
                lines.push([
                    atomPos[0] + miniVector[0] * x, atomPos[1] + miniVector[1] * x, atomPos[2] + miniVector[2] * x
                ])
            }
            for (x = 0; x < DIV; x++) {
                if (x % 3 != 0) {
                    var shape = new NGL.Shape("shape", { disableImpostor: true });
                    shape.addCylinder(lines[x], lines[x + 1], [0.205, 0.178, 0.39], 0.1);
                    var shapeComp = stage.addComponentFromObject(shape);
                    shapeComp.addRepresentation("distance");
                }
            }
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
                     color: "#16a085", aspectRatio: 8, sele: selector, assembly: stage.assembly
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
             sele: stage.residues, probeRadius: 0.75, assembly: stage.assembly
            });
        } else {
            surface.setVisibility(false)
            stage.compList[0].addRepresentation(
             "licorice", {sele: stage.residues, assembly: stage.assembly}
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
         this.value, {sele: "/0 and (not water)", assembly: stage.assembly}
        );
        stage.rep.setVisibility(true);
    })
}
