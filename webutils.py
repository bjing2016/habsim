# path_cache needs to be a list or tuple of (time, lat, long, alt)

counter = 0
def get_path_string(path_cache, color):
    global counter
    string =  "var flightPlanCoordinates" + str(counter) + " = [ \n"
    for pair in path_cache:
        string = string + "{lat: " + str(pair[1]) + ", lng: " + str(pair[2]) + "},\n"
    string = string + """
        ];
        var flightPath""" + str(counter) + """ = new google.maps.Polyline({
          path: flightPlanCoordinates"""+str(counter)+""",
          geodesic: true,
          strokeColor: '""" + color + """',
          strokeOpacity: 1.0,
          strokeWeight: 2
        });

        flightPath"""+str(counter) + """.setMap(map);"""
    
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


## Usage: simulate.py path timestamp t_offset t_neighbors, t_interval, lat, lon, ascent_rate, ascent_rate_neighbors, ascent_var, timestep_s, stop_alt
 #           0           1       2       3           4           5       6   7       8               9                    10         11          12

def get_setting_string(lat, lon, y, mo, d, h, mi, tn, ti, asc, var, an, alt, desc, max_h, step):
    return '''<script>
    document.getElementById("lat").value = ''' + str("%.4f" % lat) +''';
    document.getElementById("lon").value = ''' + str("%.4f" % lon) +''';
    document.getElementById("y").value = ''' + str(y) +''';
    document.getElementById("mo").value = ''' + str(mo)+ ''';
    document.getElementById("d").value = ''' + str(d) +''';
    document.getElementById("h").value = ''' + str(h)+ ''';
    document.getElementById("mi").value = ''' + str(mi)+ ''';
    document.getElementById("tn").value = ''' + str(tn)+ ''';
    document.getElementById("ti").value = ''' + str(ti) +''';
    document.getElementById("asc").value = ''' + str(asc)+ ''';
    document.getElementById("var").value = ''' + str(var) +''';
    document.getElementById("an").value = ''' + str(an) +''';
    document.getElementById("alt").value = ''' + str(alt) +''';
    document.getElementById("desc").value = ''' + str(desc) +''';
    document.getElementById("max_h").value = ''' + str(max_h)+ ''';
    document.getElementById("step").value = ''' + str(step) +''';
    </script>'''
    
    

#########

part1 = '''

<!DOCTYPE html>
<html>
    <head>
        <meta name="viewport" content="initial-scale=1.0, user-scalable=yes" />
        <title>Historical Batch Ascent</title>
         <style type="text/css">
 		html { height: 100% }
	      body { height: 100%; margin: 0; padding: 0 }
		
		 #info {
        position: absolute;
        width:20%;
        height:100%;
        overflow-y: scroll;
        overflow-x: scroll;
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
        <h2>Launch a balloon from the past.</h2>
        Date range supported: 2018, all timestamps. <br/>
        Locations supported: NW quadrant.<br/>
        <form>
        Lat: <input id="lat" type="text" size="8" name="lat"> <br/>
        Lon: <input id="lon" type="text" size="8" name="lon"> <br/>
        Click to select coordinates. <br/></br>
        
        If your launch location is in the continental US, the launch altitude will be the ground elevation. Otherwise, it will be 0m. <br/><br/>
            Date: <input id = "y" type="text" size="2" name="y">/<input id = "mo" type="text" size="1" name="mo">/<input id = "d" type="text" size="1" name="d"> (yyyy/mm/dd) <br/>
            Time (UTC): <input id = "h" type="text" size="1" name="h">:<input id = "mi" type="text" size="1" name="mi"><br/>
            <br/>
            Time variability: <input id = "tn" type = "text" size = "1" name = "tn"> neighbors on each side. <br/> 
            Interval <input id = "ti" type = "text" size = "1" name = "ti"> hours.<br/> <br/> 
            
            Ascent rate: <input id="asc" type="text" size="2" name="asc"> &pm; <input id="var" type="text" size="1" name="var"> m/s with
            <input id = "an" type = "text" size = "1" name = "an"> neighbors on each side, normally distributed. <br/>
            <br/>
            Stop alt: <input id = "alt" type = "text" size = "4" name = "alt">m <br/><br/>
            
            Descent rate: <input id = "desc" type = "text" size = "2" name = "desc">m/s<br/><br/>

            Simulate for <input id = "max_h" type = "text" size = "2" name = "max_h"> hours. <br/><br/>
            
            Step: <input id="step" type="text" size="4" name="step">s <br/>
	    <button formaction="https://web.stanford.edu/~bjing/cgi-bin/hist_batch.php" method = "get">Simulate</button>
	    </form>
        <br/><br/>
        Output: <br/>
'''

part3short = '''
        </script>
    <div id="map_canvas" style="width:80%; height:100%"></div>
    <div id="info" style="padding-left:2ch; padding-right: 2ch">

      <div>
   
'''

part4 = '''

      </div>
    </div>
    '''
part5 = '''
</body>
</html>

'''


#result = part1 + str(50) + "," + str(-127) + part2
#result = result + get_path_string([[30,120],[35,-120]]) + get_path_string([[30,-120],[50,80]]) + part3 + part4

#print(result)

