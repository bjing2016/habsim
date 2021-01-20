//Maps initialization
var element = document.getElementById("map");
var map = new google.maps.Map(element, {
    center: new google.maps.LatLng(37.4, -121.5),
    zoom: 9,
    mapTypeId: "OSM",
    zoomControl: false,
    gestureHandling: 'greedy'
});
google.maps.event.addListener(map, 'click', function (event) {
    displayCoordinates(event.latLng);
});
//Define OSM map type pointing at the OpenStreetMap tile server
map.mapTypes.set("OSM", new google.maps.ImageMapType({
    getTileUrl: function(coord, zoom) {
        // "Wrap" x (longitude) at 180th meridian properly
        // NB: Don't touch coord.x: because coord param is by reference, and changing its x property breaks something in Google's lib
        var tilesPerGlobe = 1 << zoom;
        var x = coord.x % tilesPerGlobe;
        if (x < 0) {
            x = tilesPerGlobe+x;
        }
        // Wrap y (latitude) in a like manner if you want to enable vertical infinite scrolling

        return "https://tile.openstreetmap.org/" + zoom + "/" + x + "/" + coord.y + ".png";
    },
    tileSize: new google.maps.Size(256, 256),
    name: "OpenStreetMap",
    maxZoom: 18
}));

// Functions for displaying things
function displayCoordinates(pnt) {
    var lat = pnt.lat();
    lat = lat.toFixed(4);
    var lng = pnt.lng();
    lng = lng.toFixed(4);
    document.getElementById("lat").value = lat;
    document.getElementById("lon").value = lng;
    getElev();
}
function getElev() {
    lat = document.getElementById("lat").value;
    lng = document.getElementById("lon").value;
    fetch(URL_ROOT + "/elev?lat=" + lat + "&lon=" + lng).then(res => res.json()).then((result) => {
        document.getElementById("alt").value = result
    })
}
function getTimeremain() {
    alt = document.getElementById("alt").value;
    eqalt = document.getElementById("equil").value;
    if (parseFloat(alt) < parseFloat(eqalt)) {
        ascr = document.getElementById("asc").value;
        console.log(alt,eqalt,ascr);
        time = (eqalt - alt)/(3600*ascr);
        console.log(time)
        document.getElementById("timeremain").textContent = time.toFixed(2) + " hr ascent remaining"
    }
    else {
        descr = document.getElementById("desc").value;
        lat = document.getElementById("lat").value;
        lng = document.getElementById("lon").value;
        fetch(URL_ROOT + "/elev?lat=" + lat + "&lon=" + lng).then(res => res.json()).then((ground) => {
            time = (alt - ground)/(3600*descr);
            document.getElementById("timeremain").textContent = time.toFixed(2) + " hr descent remaining"
        })
    }
}
async function habmc(){
    let activemissionurl = "https://stanfordssi.org/transmissions/recent";
    const proxyurl = "https://cors-anywhere.herokuapp.com/";

    await fetch(proxyurl + activemissionurl) // https://cors-anywhere.herokuapp.com/https://example.com
        .then(response => response.text())
        .then(contents => habmcshow(contents))
        .catch(() => console.log("Cant access " + activemissionurl + " response. Blocked by browser?"));
    getTimeremain();
    
}
function toTimestamp(year,month,day,hour,minute){
    var datum = new Date(Date.UTC(year,month-1,day,hour,minute));
    return datum.getTime()/1000;
}

function checkNumPos(numlist){
    for (var each in numlist){
        if(isNaN(numlist[each]) || Math.sign(numlist[each]) === -1 || !numlist[each]){
            alert("ATTENTION: All values should be positive and numbers, check your inputs again!");
            return false;
        }
    }
    return true;
}

function checkasc(asc,alt,equil){
    if(alt<equil && asc==="0"){
        alert("ATTENTION: Ascent rate is 0 while balloon altitude is below its descent ready altitude");
        return false;
    }
    return true;
}

function habmcshow(data){
    let jsondata = JSON.parse(data);
    let checkmsn = activeMissions[CURRENT_MISSION];
    for (let transmission in jsondata) {
        //console.log(activeMissions[jsondata[transmission]['mission']]);
        //console.log()

        if(jsondata[transmission]['mission'] === checkmsn){
            console.log(jsondata[transmission]);
            habmcshoweach(jsondata[transmission]);
        }
    }

}

function habmcshoweach(data2){
    let datetime = data2["Human Time"];
    var res = (datetime.substring(0,11)).split("-");
    var res2 = (datetime.substring(11,20)).split(":");
    var hourutc = parseInt(res2[0]) + 7;// Fix this for daylight savings...
    if(hourutc >= 24){
        document.getElementById("hr").value = hourutc - 24;
        document.getElementById("day").value = parseInt(res[2]) + 1;
    }
    else{
        document.getElementById("hr").value = hourutc;
        document.getElementById("day").value = parseInt(res[2]);
    }
    document.getElementById("mn").value = parseInt(res2[1]);

    console.log(res2);

    document.getElementById("yr").value = parseInt(res[0]);
    document.getElementById("mo").value = parseInt(res[1]);
    document.getElementById("lat").value = lat = parseFloat(data2["latitude"]);
    document.getElementById("lon").value = lon = parseFloat(data2["longitude"]);
    position = {
        lat: lat,
        lng: lon,
    };
    var circle = new google.maps.Circle({
        strokeColor: '#FF0000',
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: '#FF0000',
        fillOpacity: 0.35,
        map: map,
        center: position,
        radius: 5000,
        clickable: true
    });
    //var formattedTime = hours + ':' + minutes.substr(-2) + ':' + seconds.substr(-2);
    var infowindow = new google.maps.InfoWindow({
        content: "Altitude: " + data2["altitude_gps"] + " Ground speed: " + data2["groundSpeed"] + data2["direction"] + " Ascent rate " + data2["ascentRate"]
    });

    //{"Human Time":"2019-10-05 14:47:14 -0700","transmit_time":1570312034000,"internal_temp":"-18.6","pressure":"  9632","altitude_barometer":"16002","latitude":"  37.082","longitude":"-119.419","altitude_gps":"16892","ballast_time":"0","vent_time":"0","iridium_latitude":"37.1840","iridium_longitude":"-119.5492","iridium_cep":5.0,"imei":"300234067160720","momsn":"93","id":19710,"updated_at":"2019-10-05 14:47:18 -0700","flightTime":15134,"batteryPercent":"NaN","ballastRemaining":0.0,"ballastPercent":"NaN","filtered_iridium_lat":36.911748,"filtered_iridium_lon":-120.754041,"raw_data":"2d31382e362c2020393633322c31363030322c202033372e3038322c2d3131392e3431392c31363839322c302c30","mission":66,"ascentRate":-0.03,"groundSpeed":8.88,"direction":"NORTH-EAST"}

    circle.addListener("mouseover", function () {
        infowindow.setPosition(circle.getCenter());
        infowindow.open(map);
    });
    circle.addListener("mouseout", function () {
        infowindow.close(map);
    });
    map.panTo(new google.maps.LatLng(lat, lon));

    alt = parseFloat(data2["altitude_gps"]);
    document.getElementById("alt").value = alt;
    rate = parseFloat(data2["ascentRate"]);
    console.log(rate)
    if(rate > 0){
        document.getElementById("asc").value = rate;
    }
    else {
        // This order matters because on standard profile there is no eqtime
        document.getElementById("equil").value = alt;
        document.getElementById("desc").value = -rate;
        document.getElementById("eqtime").value = 0;
    }
}
