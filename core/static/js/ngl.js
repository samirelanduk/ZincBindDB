function drawNgl(code, representations, zoom) {
    stage = new NGL.Stage("ngl-container", {backgroundColor: "#ffffff"});
    stage.viewer.container.addEventListener("dblclick", function () {
        stage.toggleFullscreen();
    });
    function handleResize () {
      stage.handleResize();
    }
    window.addEventListener("orientationchange", handleResize, false);
    window.addEventListener("resize", handleResize, false);
    var load = NGL.getQuery("load");
    if (load) stage.loadFile(load, );

    stage.loadFile("rcsb://" + code + ".mmtf").then(function(component) {

        stage.rep = component.addRepresentation("cartoon", {sele: "/0"});

        if (representations) {
            for (var i = 0; i < representations.length; i++) {
                component.addRepresentation(representations[i][0], representations[i][1]);
            }
        }
        if (zoom) {
            component.autoView(representations[1][1].sele);
        } else {
            component.autoView();
        }

    });
    stage.metals = representations[0][1].sele;
    stage.residues = representations[1][1].sele;
    stage.residueColors = {};
    return stage;
}

function drawWholePdb(code, metals, residues) {
    drawNgl(code, [
        ["ball+stick", {sele: metals, aspectRatio: 8}],
        ["licorice", {sele: residues}],
        ["contact", {sele: metals + " or " + residues}]
    ], false);
}

function drawZincSite(code, metals, residues) {
    var stage = drawNgl(code, [
        ["ball+stick", {sele: metals, aspectRatio: 8}],
        ["licorice", {sele: residues}],
        ["contact", {sele: metals + " or " + residues}]
    ], true);
}

function setUpControls() {
    $("#colorPicker").change(function(e) {
        var color = $('input[type=color]').val();
        $("canvas").css("background-color", color);
    })
    var surface;
    $(".toggle-switch").click(function(e) {
        this.classList.toggle('active');

        if ($(this).hasClass("active")) {
            surface = stage.compList[0].addRepresentation("surface", {sele: stage.residues, probeRadius: 1});
        } else {
            surface.setVisibility(false)
            stage.compList[0].addRepresentation("licorice", {sele: stage.residues});

        }
    })

    $(".backbone").change(function(e) {
        stage.rep.setVisibility(false);
        stage.rep = stage.compList[0].addRepresentation(this.value, {sele: "/0"});
        stage.rep.setVisibility(true);
    })

    $(".residue").each(function(i) {
        $(this).click(function(e) {
            if ($(this).hasClass("active")) {
                $(this).removeClass("active");
                stage.residueColors[$(this).attr("data-ngl")].setVisibility(false);
            } else {
                $(this).addClass("active");
                stage.residueColors[$(this).attr("data-ngl")] = stage.compList[0].addRepresentation("licorice", {color: "#16a085", sele: $(this).attr("data-ngl")});
            }
        });
    });

    $(".metal").each(function(i) {
        $(this).click(function(e) {
            if ($(this).hasClass("active")) {
                $(this).removeClass("active");
                stage.residueColors[$(this).attr("data-ngl")].setVisibility(false);
            } else {
                $(this).addClass("active");
                stage.residueColors[$(this).attr("data-ngl")] = stage.compList[0].addRepresentation("ball+stick", {color: "#16a085", aspectRatio: 8, sele: $(this).attr("data-ngl")});
            }
        });
    });
}
