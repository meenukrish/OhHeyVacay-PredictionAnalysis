// Function to build a piechart 
function buildPieChart(airline, month, origin, destination) {
    // Print to test the selection in console
    console.log("Building Pie Chart for airline: " + airline);
    // Go to url to fetch json data to build pie chart 
    d3.json("/visualize/" + month + "/" + airline + "/" + origin + "/" + destination).then(function(chartData) {
        // If no data available for selected route and airline display the message below
        if (Object.keys(chartData).length === 0) {
            var chart = d3.select("#pie");
            chart.html("No routes available for your flight preference");
            return;
        }

         Highcharts.setOptions({
  "colors": ["#00AACC", "#FF4E00", "#B90000", "#5F9B0A", "#CD6723"],
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
    "align": "left"
  },
  "subtitle": {
    "align": "left"
  },
  "legend": {
    "align": "right",
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
});
        Highcharts.chart('pie', {
            chart: {
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false,
                type: 'pie'
            },
            title: {
                text: 'Arrival delay breakdown by causes for airline for your flight preference'  
            },
            tooltip: {
                pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: true,
                        format: '<b>{point.name}</b>: {point.percentage:.1f} %',
                        style: {
                            color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                        }
                    }
                }
            },
            series: [{
                name: 'Delay Causes',
                colorByPoint: true,
                data: [{
                    name: 'Carrier Delay',
                    y: chartData['CarrierDelay'],
                    sliced: true,
                    selected: true
                }, {
                    name: 'Weather Delay',
                    y: chartData['WeatherDelay']
                }, {
                    name: 'National Airspace Delay',
                    y: chartData['NASDelay']
                }, {
                    name: 'Security Delay',
                    y: chartData['SecurityDelay']
                }, {
                    name: 'Late Aircraft Delay',
                    y: chartData['LateAircraftDelay']
                }, {
                    name: 'On Time Arrival',
                    y: chartData['OnTime']
                }]
            }]
        });
    });
}

// Function to run when the submit button is clicked
function submitted() {
    // Get current user selection values from the dropdown list.
    // These values are month/airport/airline codes and not text values
    // displayed on the dropdown.
    

    month = d3.select("#selMonth").node().value;
    origin = d3.select("#selOrigin").node().value;
    destination = d3.select("#selDestination").node().value;
    airline = d3.select("#selAirline").node().value;
    ontimeSelected = d3.select('input[name="ontime"]:checked').node().value;

    // if (origin == destination)
    // {
    //  window.alert("Same airports selected")
    // }
    // else
    // {

        if (ontimeSelected === "ontime") {    
        // Convert airline code from the user selection to airline name. Query api
        // for airline name for the airline code.
        var airlineName = "unknown";
        d3.json("/getAirlineName/" + airline).then(function(airlineNameReturned) {
            airlineName = airlineNameReturned;

            console.log("You chose to travel in the month of " + month + " from " + origin + " to " + destination
                + " on airline " + airlineName);
            // Arrival delay prediction will be displayed here in html
            var tbody = d3.select('tbody');
            var rdata = d3.select('#recommended-data');
            var pdata = d3.select('#prediction-data');
            // Pie chart of arrival delay causes will be displayed here in html
            var chart = d3.select("#pie");

            tbody.html(""); // Clear out previous prediction data
            rdata.html("");
            pdata.html("");
            chart.html("");
            // Check user selection for the ontime vs fares radio button.
            ///deleted if from here 
                // Go to url to fetch json data to predict
                d3.json("/predict/" + month + "/" + origin + "/" + destination).then(function(predictions) {
                    // If api returned zero rows for the selected routes, it means there's no data for
                    // any airline on that route. 
                    if (Object.keys(predictions).length === 0) {
                        pdata.html("No data available for the chosen route");
                    } else {
                        // If we don't have a prediction for user airline selection, display that at the top
                        // of prediction table, otherwise display prediction value.
                        if (!(airlineName in predictions)) {
                            pdata.append("p").text(`Arrival delay predictions unavailable for ${airlineName}`);
                        } else {
                            pdata.append("p").text(`Predicted arrival delay for selected airline ${airlineName} is: ${predictions[airlineName]} minutes`);
                        }
                        // To sort airlines by predicted values, create a list of airline-prediction pairs.
                        // Sort them by prediction.
                        var sortedPredict = [];
                        Object.keys(predictions).forEach(
                          function(predAirline) {
                            sortedPredict.push([predAirline, predictions[predAirline]]);
                        });

                        sortedPredict.sort(function(a,b) {
                            return a[1]-b[1];
                        });
                        // Display airline and arrival delay prediction in prediction sorted order.
                        d3.select("#recommended-data").html(`<strong>Recommended Airline:-</strong><br>${sortedPredict[0]} minutes arrival delay `)
                        var sortedPlength = sortedPredict.length
                        for (var i = 0; i<sortedPlength; i++){
                            console.log(sortedPredict[i])
                            if (sortedPredict[i][0] === airlineName){
                                tbody.append("tr").html(`<td style="background-color:yellow">${sortedPredict[i][0]}</td><td style="background-color:yellow"> ${sortedPredict[i][1]} minutes</td>`);
                               }
                               else
                               {
                                tbody.append("tr").html(`<td>${sortedPredict[i][0]}</td><td> ${sortedPredict[i][1]} minutes</td>`);
                               }
                        }
                        
                        buildPieChart(airline, month, origin, destination);

                }

            });
        });
     } 
    else {
            console.log("I am in fare portion")
            // / Fare charts!
            predictfarejs();
        }
    // } //origin==destination else    
}

// Function to load the data when the app.py is loaded in Flask with the suggested input values
function init() {
    // Initialize month dropdown selector with month-value pairs.
    var monthSelector = d3.select("#selMonth");
           
    d3.json("/month").then((months) => {
        Object.entries(months).forEach(([month, monthId]) => {
        monthSelector
            .append("option")
            .text(month)
            .property("value", monthId); 
        });
    });
    
    
    // Initialize origin airport selector with airport-airportId pairs. Query api
    // for the airport-airportId values.
    var originSelector = d3.select("#selOrigin")
            .property("selected", "SFO");
    d3.json("/airports").then((airports) => {
        Object.entries(airports).forEach(([airport, airportId]) => {
        originSelector
            .append("option")
            .text(airport)
            .property("value", airportId); 
        });
    });

    // Initialize destination airport selector with airport-airportId pairs. Query api
    // for the airport-airportId values.
    var destSelector = d3.select("#selDestination")
            .property("selected", "BOS");
    d3.json("/airports").then((airports) => {
        Object.entries(airports).forEach(([airport, airportId]) => {
        destSelector
            .append("option")
            .text(airport)
            .property("value", airportId); 
        });
    });
    // Initialize airlines selector with airline-airlineId pairs. Query api for the pairs.
    var airlineSelector = d3.select("#selAirline")
            .property("selected", "UA");
    d3.json("/airline").then((airline) => {
        Object.entries(airline).forEach(([airline, airlineId]) => {
        airlineSelector
            .append("option")
            .text(airline)
            .property("value", airlineId); 
        });
    });
    // Function call submitted when the submit button is clicked after inputting values
    submitted();
}

init();