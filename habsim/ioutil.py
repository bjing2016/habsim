import random
import math
class RandomColorGenerator:
    '''
    Generates random web-compatible colors.
    Can be accessed like a list.
    '''
    def __init__(self):
        pass
        
    def __getitem__(self, key):
        red, green, blue = random.choices(["00", "33", "66", "99", "CC"], k=3)
        return '#' + red + green + blue

    def __len__(self):
        return 10 ** 10

def get_html_marker_string(lat, lon, label, title):
    '''
    Internal method. Do not use.
    '''
    return '''var marker = new google.maps.Marker({
            position: {lat: ''' + str(lat)+''', lng: ''' + str(lon) + '''},
            label: " ''' + label + ''' ",
            title:" ''' + title + ''' "
        });
        // To add the marker to the map, call setMap();
        marker.setMap(map);
    '''

def get_html_path_string(path_cache, color, counter, opacity=1.0, weight=2):
    '''
    Internal method. Do not use.
    '''
    string =  "var flightPlanCoordinates" + str(counter) + " = [ \n"
    for pair in path_cache:
        string = string + "{lat: " + str(pair[1]) + ", lng: " + str(pair[2]) + "},\n"
    string = string + """
        ];
        var flightPath""" + str(counter) + """ = new google.maps.Polyline({
          path: flightPlanCoordinates"""+str(counter)+""",
          geodesic: true,
          strokeColor: '""" + color + """',
          strokeOpacity: """ + str(opacity) + """,
          strokeWeight: """ + str(weight) + """
        });

        flightPath"""+str(counter) + """.setMap(map);"""
    return string

def get_circle_string(lat, lon, radius, content, strokeColor, strokeOpacity, strokeWeight, fillColor, fillOpacity):
    string = """
    var circle = new google.maps.Circle({
        strokeColor: '""" + strokeColor + """',
        strokeOpacity: """ + str(strokeOpacity) +""",
        strokeWeight: """ + str(strokeWeight) + """,
        fillColor: '""" + fillColor + """',
        fillOpacity: """ + str(fillOpacity) + """,
        map: map,
        center: {lat: """ + str(lat) + """, lng: """ + str(lon) + """},
        radius: """+str(radius)+''',
        clickable: true
    });
    '''
    if content is None: return string
    string+= '''
    var infowindow = new google.maps.InfoWindow({
        content: "'''+ content + '''"
    });
    circle.addListener("mouseover", function () {
        infowindow.setPosition(circle.getCenter());
        infowindow.open(map);
    });
    circle.addListener("mouseout", function () {
        infowindow.close(map);
    });
    '''
    return string


default_colors = ["#000000", "#FF0000", "#008000", "#800000", "#808000"]
class WebPlot:
    '''
    A WebPlot writes an HTML file where trajectories can be viewed in an OpenStreetMap interface.
    '''
    def __init__(self):
        self.pathstring = ""
        self.counter = 0

    def add(self, trajectories, colors = default_colors, opacity=1.0, weight=2):
        '''
        Adds a list of trajectories. If list is longer than 5, colors must be specified.
        Whenever this method is called, the list of colors is used from the beginning.
        Therefore passing in segments seperately is not the same as passing in a list.
        '''
        if len(trajectories) > len(colors):
            raise Exception("Longest trajectory longer than number of colors.")
        
        for i in range(len(trajectories)):
            self.pathstring += get_html_path_string(trajectories[i], colors[i], self.counter, opacity, weight)
            self.counter += 1

    def marker(self, lat, lon, label="", title=""):
        '''
        Adds a marker with a visible label and a title shown upon mouseover.
        '''
        self.pathstring += get_html_marker_string(lat, lon, label, title)

    def circle(self, lat, lon, radius, content=None, strokeColor='#FF0000', strokeOpacity=1, strokeWeight=1, fillColor='#FF0000', fillOpacity=0.35):
        '''
        Adds a circle with content shown upon mouseover and radius approximately in meters.
        '''
        self.pathstring += get_circle_string(lat, lon, radius, content, strokeColor, strokeOpacity, strokeWeight, fillColor, fillOpacity)
        

    def origin(self, lat, lon, zoom=7):
        '''
        Sets the origin of the plot. Must be called.
        '''
        self.lat = lat
        self.lon = lon
        self.zoom = zoom
    
    def save(self, name):
        '''
        Writes file to disk.
        '''
        f = open(name, "w")
        f.write(part1 + str(self.lat) + "," + str(self.lon) + "),zoom:" + str(self.zoom))
        f.write(part2)
        f.write(self.pathstring)
        f.write(part3)

#########

part1 = '''

<!DOCTYPE html>
<html>
    <head>
        <meta name="viewport" content="initial-scale=1.0, user-scalable=yes" />
         <style type="text/css">
 		html { height: 100% }
	    body { height: 100%; margin: 0; padding: 0 }            
		#map{
                height: 100%;
                width: 100%;
                margin: 0;
                padding: 0;
            }
        .small {
            position: absolute;
            top: 20px;
            right: 60px;
            }
        </style> 
    </head>
    <body>
        <div id="map" style="float: left;"></div>
        <div class="small"><span id="text"></span><span id="elev"></span></div>       
        <!-- bring in the google maps library -->
        <script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?sensor=false"></script>
        <script type="text/javascript">
            //Google maps API initialisation
            var element = document.getElementById("map");
            var map = new google.maps.Map(element, {
                center: new google.maps.LatLng('''
                
part2 = ''' ,
                mapTypeId: "OSM",      
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
''' 

part3 = '''
        function displayCoordinates(pnt) {
            var lat = pnt.lat();
            lat = lat.toFixed(4);
            var lng = pnt.lng();
            lng = lng.toFixed(4);
            elev = getElev(lat, lng)
            document.getElementById("text").textContent = String(lat) + "," + String(lng) + " "
        }
        function getElev(lat, lng) {
            fetch("https://predict.stanfordssi.org/elev?lat=" + lat + "&lon=" + lng).then(res => res.json()).then((result) => {
                document.getElementById("elev").textContent = result + " m"
            })
        }
        </script>
    <div id="map_canvas" style="width:80%; height:100%"></div>
    <div id="info" style="padding-left:2ch; padding-right: 2ch">

      <div>
      </div>
    </div>
</body>
</html>
'''