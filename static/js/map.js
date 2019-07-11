
function buildmap(airportdata, airlinedata)
{

  console.log("Inside map.js")
  console.log(`${airportdata}`);
  console.log(`${airlinedata}`)

  var colors =["#00AACC", "#FF4E00", "#B90000", "#5F9B0A", "#CD6723"]; 
//SET THE THEME
Highcharts.getOptions().colors = Highcharts.map(colors, function(color) {return {
  radialGradient: {
      cx: 0.5,
      cy: 0.3,
      r: 0.7
  },
  stops: [
      [0, color],
      [1, Highcharts.Color(color).brighten(-0.3).get('rgb')] // darken
  ]
}});

if (!Highcharts.charts.length) {
  
console.log("inside set options")
Highcharts.setOptions({
  // "colors": ["#00AACC", "#FF4E00", "#B90000", "#5F9B0A", "#CD6723"]
//   "colors": Highcharts.map(Highcharts.getOptions().colors, function (color) {
//     return {
//         radialGradient: {
//             cx: 0.5,
//             cy: 0.3,
//             r: 0.7
//         },
//         stops: [
//             [0, color],
//             [1, Highcharts.Color(color).brighten(-0.3).get('rgb')] // darken
//         ]
//     };
// }),
  "chart": {
    "backgroundColor": {
      "linearGradient": [
        0,
        0,
        0,
        150
      ],
      "stops": [
        [
          0,
          "#CAE1F4"
        ],
        [
          1,
          "#EEEEEE"
        ]
      ]
    },
    "style": {
      "fontFamily": "Open Sans"
    }
  },
  "title": {
    "color":"#CD6723",
    "align": "center"
  },
  "subtitle": {
    "align": "center"
  },
  "legend": {
    "align": "center",
    "verticalAlign": "bottom"
  },
  "xAxis": {
    "gridLineWidth": 1,
    "gridLineColor": "#F3F3F3",
    "lineColor": "#F3F3F3",
    "minorGridLineColor": "#F3F3F3",
    "tickColor": "#F3F3F3",
    "tickWidth": 1
  },
  "yAxis": {
    "gridLineColor": "#F3F3F3",
    "lineColor": "#F3F3F3",
    "minorGridLineColor": "#F3F3F3",
    "tickColor": "#F3F3F3",
    "tickWidth": 1
  }
})

}


// Initialize the chart
var chart = Highcharts.mapChart('pie', {

    title: {
        text: 'Best Flight Fare comparison'
    },

    subtitle: {
      text: 'Click on the flight path to see more details!'
  },

    legend: {
            title: {
                style: {
                    color: ( // theme
                        Highcharts.defaultOptions &&
                        Highcharts.defaultOptions.legend &&
                        Highcharts.defaultOptions.legend.title &&
                        Highcharts.defaultOptions.legend.title.style &&
                        Highcharts.defaultOptions.legend.title.style.color
                    ) || 'black'
                }
            }
        },

    mapNavigation: {
        enabled: true
    },

    tooltip: {
        formatter: function () {
            return '<strong>'+this.point.value +'</strong>'+ (
                this.point.lat ? '<br>Lat: ' + this.point.lat +'<br>'+ ' Lng: ' + this.point.lon : '');
        }
    },

     
    plotOptions: {
        series: {
            marker: {
                fillColor:'#99bbff',
                lineWidth: 2,
                lineColor:Highcharts.getOptions().colors[1] || null            
            }
                     
        }
                
    },

    series: [
        {
        // Use the gb-all map with no data as a basemap
        mapData: Highcharts.maps['countries/us/custom/us-all-territories'],
        name: 'Basemap',
        borderColor:'#707070',
        nullColor: null,   //'#0088cc',   // the map fill color
        showInLegend: false
    }, 
    {
        name: 'Separators',
        type: 'mapline',
        data: Highcharts.geojson(Highcharts.maps['countries/us/custom/us-all-territories'], 'mapline'),
        color: '#0000cc',
        showInLegend: false,
        enableMouseTracking: false
    },  
    
    {
        // Specify cities using lat/lon
        type: 'mappoint',
        name: 'Airports',
        dataLabels: {
            format: '{point.value}'
        },
        // Use id instead of name to allow for referencing points later using
        // chart.get
        data: airportdata
    }],
    
    responsive: {
        rules: [{
            condition: {
                maxWidth: 700
            },
            chartOptions: {
                chart: {
                    className: 'small-chart'
                }
            }
        }]
    },


});

// Function to return an SVG path between two points, with an arc
function pointsToPath(from, to, invertArc) {
    var arcPointX = (from.x + to.x) / (invertArc ? 2.4 : 1.6),
        arcPointY = (from.y + to.y) / (invertArc ? 2.4 : 1.6);
    return 'M' + from.x + ',' + from.y + 'Q' + arcPointX + ' ' + arcPointY +
            ',' + to.x + ' ' + to.y;
}

var OriginPoint = chart.get(0)  //Origin
var DestinationPoint = chart.get(1) //destination

/// this the retrieving the text.
var airnames = airlinedata.map(function(d){return(d.airname)})
var airimgs = airlinedata.map(function(d){return(d.airimg)})  
var predvals = airlinedata.map(function(d){return(d.predval)}) 

//Adding the chosen and recommended paths
for (i=0; i<airlinedata.length;i++)
{

var htmlstr = `<strong>Airline Name:</strong><br> ${airnames[i]} <br><strong>Predicted value :</strong> $${predvals[i]}`    
var imagepath = airimgs[i];

chart.addSeries({
    name: airnames[i],
    type: "mapline",
    lineWidth: 3, //thickness of the path
    color: Highcharts.getOptions().colors[i+3],   //+3
    data: [{
        value:htmlstr,
        name:"SFO-DEN",
        dimg: imagepath,
        path: pointsToPath(OriginPoint, DestinationPoint, i)    // destination
    } ], 
    animation:{duration:"3000"}, 
    cursor: "pointer", 
    events:{
        click: function(e)
         {  
           var text =  '<strong>'+e.point.value +'</strong>';
            var limg = e.point.dimg;
          
           if (!this.chart.clickLabel & !this.chart.clickimage) 
           {
            this.chart.clickLabel = this.chart.renderer.label(text,500, 150)
                                    .css({ width: '180px', color: '003cb3' })   //003cb3
                                    .add();
            this.chart.clickimage =  this.chart.renderer.image(limg,500, 100, 100, 30).add()
            } 
            else 
            {
                this.chart.clickLabel.attr({ text: text});
                
                this.chart.clickimage.attr({href:limg});
            }
        },
            
    }
       
});
}

}


