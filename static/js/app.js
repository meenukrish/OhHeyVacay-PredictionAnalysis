
function predictfarejs()
{
  // console.log("I am here")
  var qtr; 
  var month = d3.select("#selMonth").node().value;
  if (month=="Jan" | month=="Feb"|month=="Mar"){ qtr = 1 }
      else if (month=="Apr" | month=="May"|month=="June") { qtr = 2  }
      else if (month=="Jul" | month=="Aug"|month=="Sep") { qtr = 3 }
      else { qtr = 4 }
  
  
 var selorigin = parseInt(d3.select("#selOrigin").node().value);
 var seldest = parseInt(d3.select("#selDestination").node().value);
 var selchosenairline = parseInt(d3.select("#selAirline").node().value);


 if (selorigin ==10397){origin = 'ATL'}
 else if(selorigin==10721){origin = 'BOS'}
 else if(selorigin==11259){origin = 'DAL'}
 else if(selorigin==11292){origin = 'DEN'}
 else if(selorigin==11697){origin = 'FLL'}
 else if(selorigin==12478){origin = 'JFK'}
 else if(selorigin==12889){origin = 'LAS'}
 else if(selorigin==12892){origin = 'LAX'}
 else if(selorigin==14057){origin = 'PDX'}
 else {origin = 'SFO'};

console.log(`origin${origin}`)

 
 var dest;

 if (seldest ==10397){dest = 'ATL'}
 else if(seldest==10721){dest = 'BOS'}
 else if(seldest==11259){dest = 'DAL'}
 else if(seldest==11292){dest = 'DEN'}
 else if(seldest==11697){dest = 'FLL'}
 else if(seldest==12478){dest = 'JFK'}
 else if(seldest==12889){dest = 'LAS'}
 else if(seldest==12892){dest = 'LAX'}
 else if(seldest==14057){dest = 'PDX'}
 else {dest = 'SFO'};

 console.log(`destination${dest}`)

 
 var chosenairline;

 if (selchosenairline == 19805){chosenairline = 'AA'; selairname = "American Airlines Inc.";}
 else if(selchosenairline == 19930){chosenairline = 'AS'; selairname = "Alaska Airlines Inc.";}
 else if(selchosenairline == 20409){chosenairline = 'B6'; selairname = "JetBlue Airways";}
 else if(selchosenairline == 19790){chosenairline = 'DL'; selairname = "Delta Air Lines Inc.";}
 else if(selchosenairline == 20366){chosenairline = 'EV'; selairname = "ExpressJet Airlines LLC";}
 else if(selchosenairline == 20436){chosenairline = 'F9'; selairname = "Frontier Airlines Inc.";}
 else if(selchosenairline == 19690){chosenairline = 'HA'; selairname = "Hawaiian Airlines Inc.";}
 else if(selchosenairline == 20304){chosenairline = 'OO'; selairname = "SkyWest Airlines Inc.";}
 else if(selchosenairline == 19977){chosenairline = 'UA'; selairname = "United Air Lines Inc.";}
 else {chosenairline = 'WN'; selairname = "Southwest Airlines Co.";};

 console.log(`chosen airline ${chosenairline}`)


if (origin == dest)
{
  window.alert("You cannot choose the same airport for Origin and Destination")
}
else
{
    var tbody = d3.select("tbody")

    d3.select("#prediction-data").text("");
    d3.select("#recommended-data").text("Loading the predictions...");
    d3.select("#pie").html("");
    
    tbody.text(""); 

    // PREDICITING THE FARE FOR THE CHOSEN AIRLINE
    predicturl =`/predictfare/${qtr}/${origin}/${dest}/${chosenairline}`;

    var chosenfare ;

    d3.json(predicturl).then(function(fare)
    {
    var predictdiv = d3.select("#prediction-data");
    chosenfare = fare;
    predictdiv.text(`Predicted Fare for ${selairname}: $${fare}`) ;  


    //  PREDICTING THE FARE COST FOR OTHER AIRLINES AND DISPLAY THE RANKING. 

    allpredicturl =`/predictallfare/${qtr}/${origin}/${dest}/${chosenairline}`;

    d3.json(allpredicturl).then(function(allfare)
    {

    allfaredata = JSON.parse(JSON.stringify(allfare))


    var count = 1
    var recommendairline; 
    var recairfare; 

    Object.entries(allfaredata.Predicted_Average_Fare).forEach(([key, value]) => 
    {
      if(count==1){

        d3.select("#recommended-data").html(`<strong>Recommended Airline:</strong><br>${key} <br>Fare:$${value}`)
        recommendairline = key; 
        recairfare = value;
        count += 1
      }
      // HIGHLIGHTING THE <tr> TO SHOW THE RANKING
      if(value == chosenfare)
      {
        tbody.append("tr").html(`<td style="background-color:yellow">${key}</td><td style="background-color:yellow">$${value}</td>`)
      }
      else
      { 
        tbody.append("tr").html(`<td>${key}</td><td id="rankfare">$${value}</td>`)
      }

    });


   //// 

    
// FORM THE URL FOR GETLATLNG API CALL

var getoriginlatlngurl = `/getlatlng/${origin}`;  
var getdestlatlngurl = `/getlatlng/${dest}`; //    /dest`
var originlat;
var originlng; 
var destlat;
var destlng

d3.json(getoriginlatlngurl).then(function(latlnglist)
{
  originlat = parseFloat(latlnglist[0])
  originlng = parseFloat(latlnglist[1])


d3.json(getdestlatlngurl).then(function(latlnglist)
{
  destlat = parseFloat(latlnglist[0])
  destlng = parseFloat(latlnglist[1])



function chooseimg(airline){

if (airline == 'American Airlines Inc' || airline == 'AA' ) { return 'static/images/AmericanAirline.png'  }
else if (airline == 'Alaska Airlines Inc.' || airline == 'AS') { return 'static/images/Alaska.png' }
else if (airline == 'JetBlue Airways' || airline == 'B6') { return 'static/images/JetBlue.png' }
else if (airline == 'Delta Air Lines Inc.' || airline == 'DL') { return 'static/images/Delta AirLines.png'}
else if (airline == 'ExpressJet Airlines LLC' || airline == 'EV') { return 'static/images/ExpressJet Airlines.png' }
else if (airline == 'Frontier Airlines Inc.' || airline == 'F9') { return 'static/images/Frontier Airlines.png'}
else if (airline == 'Hawaiian Airlines Inc.' || airline == 'HA') { return 'static/images/hawaiian Airline.png'}
else if (airline == 'SkyWest Airlines Inc.' || airline == 'OO') { return 'static/images/SkyWest Airlines.png' }
else if (airline == 'United Air Lines Inc.' || airline == 'UA') { return 'static/images/united.png' }
else if (airline == 'Southwest Airlines Co.' || airline == 'WN') { return 'static/images/Southwest Airlines.png' }


}



airportdata = [{
  id:0,
  value:origin,
  lat: originlat,
  lon: originlng
}, 
{
  id:1,
  value:dest,  
  lat: destlat,
  lon: destlng
}]

airlinedata = [
{
  airname:recommendairline, 
  airimg:chooseimg(recommendairline), 
  predval:recairfare
}, 
{
  airname: selairname, 
  airimg:chooseimg(chosenairline), 
  predval: chosenfare
}];

// airlinedata.forEach(function(d){console.log(d)})

//  d3.select("#pie").html("")

console.log(`airport data ${airportdata}`);
console.log(`airlinedata ${airlinedata}`);

buildmap(airportdata, airlinedata);


}); //dest d3latlng

}); //origin d3latlng
 
}); //d3 end

});//d3 end

} //end of else (origin == dest)

 
} // end of predictfarejs()



