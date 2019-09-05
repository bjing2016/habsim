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
    fetch("https://predict.stanfordssi.org/elev?lat=" + lat + "&lon=" + lng).then(res => res.json()).then((result) => {
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
        fetch("https://predict.stanfordssi.org/elev?lat=" + lat + "&lon=" + lng).then(res => res.json()).then((ground) => {
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
        .catch(() => console.log("Can’t access " + activemissionurl + " response. Blocked by browser?"));
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
    let data2 = JSON.parse(data);
    console.log(data2);
    let datetime = data2["Human Time"];
    var res = (datetime.substring(0,11)).split("-");
    var res2 = (datetime.substring(11,20)).split(":");
    var hourutc = parseInt(res2[0]);
    if(hourutc >= 24){
        document.getElementById("hr").value = hourutc - 24;
    }
    else{
        document.getElementById("hr").value = hourutc;
    }
    document.getElementById("mn").value = parseInt(res2[1]);

    console.log(res2);

    document.getElementById("yr").value = parseInt(res[0]);
    document.getElementById("mo").value = parseInt(res[1]);
    document.getElementById("day").value = parseInt(res[2]);
    document.getElementById("lat").value = parseFloat(data2["latitude"]);
    document.getElementById("lon").value = parseFloat(data2["longitude"]);
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
