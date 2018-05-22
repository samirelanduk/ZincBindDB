function drawNgl(code, representations) {
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

        component.addRepresentation("cartoon", {sele: "/0"});

        if (representations) {
            for (var i = 0; i < representations.length; i++) {
                component.addRepresentation(representations[i][0], representations[i][1]);
            }
        }
        if (representations.length > 1) {
            component.autoView(representations[1][1].sele);
        } else {
            component.autoView();
        }

    });
    return stage;
}

function drawWholePdb(code, metals) {
    drawNgl(code, [
        ["ball+stick", {sele: metals, aspectRatio: 8}]
    ]);
}

function drawZincSite(code, metals, residues) {
    var stage = drawNgl(code, [
        ["ball+stick", {sele: metals, aspectRatio: 8}],
        ["licorice", {sele: residues}]
    ]);
}

function setUpControls() {
    $(".color-options").click(function(e) {
        var color = $('input[name=color]:checked').val();
        $("canvas").css("background-color", color);
    })
}
