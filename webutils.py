# path_cache needs to be a list or tuple of (lat, long)

counter = 0
def get_path_string(path_cache):
    global counter
    string =  "var flightPlanCoordinates" + str(counter) + " = [ \n"
    for pair in path_cache:
        string = string + "{lat: " + str(pair[0]) + ", lng: " + str(pair[1]) + "},\n"
    string = string + '''
        ];
        var flightPath''' + str(counter) + ''' = new google.maps.Polyline({
          path: flightPlanCoordinates'''+str(counter)+''',
          geodesic: true,
          strokeColor: '#FF0000',
          strokeOpacity: 1.0,
          strokeWeight: 2
        });

        flightPath'''+str(counter) + '''.setMap(map);'''
    
    counter = counter + 1
    return string


def get_marker_string(lat, lon, label, title):
        return '''var marker = new google.maps.Marker({
                position: {lat: ''' + str(lat)+''', lng: ''' + str(lon) + '''},
                label: " ''' + label + ''' ",
                title:" ''' + title + ''' "
            });
            // To add the marker to the map, call setMap();
            marker.setMap(map);
        '''

#########

part1 = '''

<!DOCTYPE html>
<html>
    <head>
        <meta name="viewport" content="initial-scale=1.0, user-scalable=yes" />
        <title>Historical Simple Ascent</title>
         <style type="text/css">
 		html { height: 100% }
	      body { height: 100%; margin: 0; padding: 0 }
		
		 #info {
        position: absolute;
        width:20%;
        height:100%;
        overflow-y: scroll;
        bottom:0px;
        right:0px;
        top:0px;
        background-color: white;
        border-left:1px #666 solid;
        font-family:Helvetica; }
            
		#map{
                height: 100%;
                width: 100%;
                margin: 0;
                padding: 0;
            }
  
        </style> 
    </head>
    <body>
        <div id="map" style="float: left;"></div>       
        
        
        <!-- bring in the google maps library -->
        <script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?sensor=false"></script>
        
        <script type="text/javascript">
            //Google maps API initialisation
            var element = document.getElementById("map");
 
            var map = new google.maps.Map(element, {
                center: new google.maps.LatLng('''
                
part2 = ''' ),
                zoom: 9,
                mapTypeId: "OSM",
              
            });


            google.maps.event.addListener(map, 'click', function (event) {
              displayCoordinates(event.latLng);               
            });

            function displayCoordinates(pnt) {

                var lat = pnt.lat();
                lat = lat.toFixed(4);
                var lng = pnt.lng();
                lng = lng.toFixed(4);


                document.getElementById("lat").value = lat;

                document.getElementById("lon").value = lng;


            }
 
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



''' 
part3 = '''
        </script>
<div id="map_canvas" style="width:80%; height:100%"></div>
    <div id="info" style="padding-left:2ch; padding-right: 2ch">
      <div>
        <h1>Launch a balloon from the past.</h1>

       	<form action="cgi-bin/test.php" method="get">	
		Lat: <input id="lat" type="text" size="8" name="lat"> <br/>
		Lon: <input id="lon" type="text" size="8" name="lon"> <br/><br/>
        If your launch location is in the continental US, the launch altitude will be the ground elevation. Otherwise, it will be 0m. <br/><br/>
        Timestamp: <input id = "time" type="text" size="12" name="timestamp"> <br/>yyyymmddhh (hh = 00, 06, 12, 18) <br/><br/>
				
		Ascent rate: <input id="rate" type="text" size="4" name="rate">m/s <br/>
		Timestep: <input id="timestep" type="text" size="4" name="timestep">s <br/>
		Stop alt: <input id = "alt" type = "alt" size = "4" name = "alt">m <br/> <br/>
	
	    <button formaction="cgi-bin/simple_hist_asc.php" method = "get">Simulate</button></br></br>

    
        Output: <br/>
'''
part4 = '''

	    </form>
      </div>
    </div>
</body>
</html>

'''


#result = part1 + str(50) + "," + str(-127) + part2
#result = result + get_path_string([[30,120],[35,-120]]) + get_path_string([[30,-120],[50,80]]) + part3 + part4

#print(result)

