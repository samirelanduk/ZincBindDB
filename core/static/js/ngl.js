function drawNgl(code) {
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
    if (load) stage.loadFile(load, {defaultRepresentation: true});

    stage.loadFile("rcsb://" + code + ".mmtf", {defaultRepresentation: true});
}

function setUpControls() {
    $(".color-options").click(function(e) {
        var color = $('input[name=color]:checked').val();
        $("canvas").css("background-color", color);
    })
}
