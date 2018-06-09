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
    return stage;
}

function drawWholePdb(code, metals, residues) {
    drawNgl(code, [
        ["ball+stick", {sele: metals, aspectRatio: 8}],
        ["licorice", {sele: residues}]
    ], false);
}

function drawZincSite(code, metals, residues) {
    var stage = drawNgl(code, [
        ["ball+stick", {sele: metals, aspectRatio: 8}],
        ["licorice", {sele: residues}]
    ], true);
}

function setUpControls() {
    $(".color-options").click(function(e) {
        var color = $('input[name=color]:checked').css("background-color");
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
}
