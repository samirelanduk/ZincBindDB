
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



function drawContrastChart(solvation, contrast) {
    var chart = Highcharts.chart("solvation-chart", {
    chart: {
        zoomType: "xy",
        type: "line",
        plotBorderWidth: 1,
    },
    title: {
        text: "Hydrophobic Contrast"
    },
    credits: {
        enabled: false
    },
    xAxis: [{
        crosshair: true,
        min: 0,
        max: 10,
        title: {
            useHTML: true,
            text: "Sphere radius (&#x212B;)"
        }
    }],
    yAxis: [{
        gridLineWidth: 1,
        title: {
            useHTML: true,
            text: "Average Solvation (J mol<sup>-1</sup> A<sup>-2</sup>)",
            style: {
                color: Highcharts.getOptions().colors[0]
            }
        },
        labels: {
            style: {
                color: Highcharts.getOptions().colors[0]
            }
        }
    }, {
        gridLineWidth: 0,
        title: {
            useHTML: true,
            text: "Hydrophobic Contrast Score (J mol<sup>-1</sup>)",
            style: {
                color: "#85144b"
            },
        },
        labels: {
            style: {
                color: "#85144b"
            }
        },
        opposite: true

    }],
    tooltip: {
        shared: true
    },
    legend: {
        layout: 'vertical',
        align: 'left',
        x: 80,
        verticalAlign: 'top',
        y: 55,
        floating: true,
    },
    series: [{
        name: 'solvation',
        data: solvation,
        useHTML: true,
        tooltip: {
            useHTML: true,
            valueSuffix: ' J mol<sup>-1</sup> A<sup>-2</sup>'
        },
        color: Highcharts.getOptions().colors[0]

    }, {
        name: 'contrast',
        yAxis: 1,
        data: contrast,
        tooltip: {
            valueSuffix: ' J mol<sup>-1</sup>'
        },
        color: "#85144b"
    }]
    });

}
