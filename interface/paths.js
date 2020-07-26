// Controls fetching and rendering of trajectories.

// Cache of compount paths
rawpathcache = []

// Shows a single compound path, mode unaware
function makepaths(btype, allpaths){
    rawpathcache.push(allpaths)
    for (index in allpaths) {
        var pathpoints = [];

        for (point in allpaths[index]){
                var position = {
                    lat: allpaths[index][point][1],
                    lng: allpaths[index][point][2],
                };
                pathpoints.push(position);
        }
        var drawpath = new google.maps.Polyline({
            path: pathpoints,
            geodesic: true,
            strokeColor: getcolor(index),
            strokeOpacity: 1.0,
            strokeWeight: 2
        });
        drawpath.setMap(map);
        currpaths.push(drawpath);
    }


}
function clearWaypoints() {
    //Loop through all the markers and remove
    for (var i = 0; i < circleslist.length; i++) {
        circleslist[i].setMap(null);
    }
    circleslist = [];
}

function showWaypoints() {
    for (i in rawpathcache) {
        allpaths = rawpathcache[i]
        for (index in allpaths) {
            for (point in allpaths[index]){
                (function () {
                    var position = {
                        lat: allpaths[index][point][1],
                        lng: allpaths[index][point][2],
                    };
                    if(waypointsToggle){
                        var circle = new google.maps.Circle({
                            strokeColor: getcolor(index),
                            strokeOpacity: 0.8,
                            strokeWeight: 2,
                            fillColor: getcolor(index),
                            fillOpacity: 0.35,
                            map: map,
                            center: position,
                            radius: 300,
                            clickable: true
                        });
                        circleslist.push(circle);
                        // multiplied by 1000 so that the argument is in milliseconds, not seconds.
                        var date = new Date(allpaths[index][point][0] * 1000);
                        // Hours part from the timestamp
                        var hours = date.getHours();
                        // Minutes part from the timestamp
                        var minutes = "0" + date.getMinutes();
                        // Seconds part from the timestamp
                        var seconds = "0" + date.getSeconds();

                        // Will display time in 10:30:23 format
                        var formattedTime = hours + ':' + minutes.substr(-2) + ':' + seconds.substr(-2);
                        var infowindow = new google.maps.InfoWindow({
                            content: "Altitude: " + allpaths[index][point][3] + "m \n \n \n Time: " + formattedTime
                        });
                        circle.addListener("mouseover", function () {
                            infowindow.setPosition(circle.getCenter());
                            infowindow.open(map);
                        });
                        circle.addListener("mouseout", function () {
                            infowindow.close(map);
                        });
                    }
                }());
            }
        }
    }
}


// Cache of circles
circleslist = [];

// Shows a single compound path, but is mode-aware
function showpath(path) {
    switch(btype) {
        case 'STANDARD':
            var rise = path[0];
            var equil = []
            var fall = path[2];
            var fpath = [];

            break;
        case 'ZPB':
            var rise = path[0];
            var equil = path[1]
            var fall = path[2];
            var fpath = [];
            break;

        case 'FLOAT':
            var rise = [];
            var equil = [];
            var fall = [];
            var fpath = path;
    }
    var allpaths = [rise, equil, fall, fpath];
    makepaths(btype, allpaths);

}

function getcolor(index){
    switch(index){
        case '0':
            return '#DC143C';
        case '1':
            return '#0000FF';
        case '2':
            return '#000000';
        case '3': return '#000000';
    }
}

// Cache of polyline objects
var currpaths = new Array();

// Self explanatory
async function simulate() {
    clearWaypoints();
    for (path in currpaths) {currpaths[path].setMap(null);}
    currpaths = new Array();
    rawpathcache = new Array()
    console.log("Clearing");

    allValues = [];
    var time = toTimestamp(Number(document.getElementById('yr').value),
        Number(document.getElementById('mo').value),
        Number(document.getElementById('day').value),
        Number(document.getElementById('hr').value),
        Number(document.getElementById('mn').value));
    var lat = document.getElementById('lat').value;
    var lon = document.getElementById('lon').value;
    var alt = document.getElementById('alt').value;
    var url = "";
    allValues.push(time,alt);
    switch(btype) {
        case 'STANDARD':
            // code block
            var equil = document.getElementById('equil').value;
            var asc = document.getElementById('asc').value;
            var desc = document.getElementById('desc').value;
            url = URL_ROOT + "/singlezpb?timestamp="
                + time + "&lat=" + lat + "&lon=" + lon + "&alt=" + alt + "&equil=" + equil + "&eqtime=" + 0 + "&asc=" + asc + "&desc=" + desc;
            allValues.push(equil,asc,desc);
            break;
        case 'ZPB':
            // code block
            var equil = document.getElementById('equil').value;
            var eqtime = document.getElementById('eqtime').value;
            var asc = document.getElementById('asc').value;
            var desc = document.getElementById('desc').value;
            url = URL_ROOT + "/singlezpb?timestamp="
                + time + "&lat=" + lat + "&lon=" + lon + "&alt=" + alt + "&equil=" + equil + "&eqtime=" + eqtime + "&asc=" + asc + "&desc=" + desc
            allValues.push(equil,eqtime,asc,desc);
            break;
        case 'FLOAT':
            // code block
            var coeff = document.getElementById('coeff').value;
            var step = document.getElementById('step').value;
            var dur = document.getElementById('dur').value;
            url = URL_ROOT + "/singlepredict?timestamp="
                + time + "&lat=" + lat + "&lon=" + lon + "&alt=" + alt + "&rate=0&coeff=" + coeff + "&step=" + step + "&dur=" + dur
            allValues.push(coeff,step,dur);
            break;
    }
    var onlyonce = true;
    if(checkNumPos(allValues) && checkasc(asc,alt,equil)){
        for (i = 1; i < 21; i++) {
            var url2 = url + "&model=" + i;
            console.log(url2);
            await fetch(url2).then(res => res.json()).then(function(resjson){
                if(resjson==="error"){
                    if(onlyonce) {
                        alert("ERROR: Please make sure your entire flight is within 378 hours of the present model run.");
                        onlyonce = false;
                    }
                    //break;
                 }
                else {
                    showpath(resjson);
                }
            });
            if (Number(document.getElementById('yr').value) < 2019){
                console.log("Historical flight, breaking after one run");
                break;
            }
        }
        onlyonce = true;
    }
    if (waypointsToggle) {showWaypoints()}
}
