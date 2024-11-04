# Python Flask, Socket.io and Google Charts
[![DOI](https://zenodo.org/badge/733807414.svg)](https://zenodo.org/doi/10.5281/zenodo.10409021)

This example shows how measurement data can be displayed in a web application using Google Chart so that the data is updated in real time.
The program datageneratorclient.py generates simulated measurement data and sends it to the server program. The server program measserver.py, implemented in Flash, receives the measurements and passes them to an html page where they are displayed with Google Charts. The server program communicates with the html page using socket.io.

## Files

### datageneratorclient.py

The Python program datageneratorclient.py generates simulated measurement data. The spatial coordinates of the imaginary device are generated using trigonometric functions:

```python
    measurement = { }
    measurement['time'] = t
    measurement['x'] = 5 * math.cos(t) + (random.random() * 2 - 1)
    measurement['y'] = 6 * math.sin(t) + (random.random() * 2 - 1)
    measurement['z'] = (random.random() * 2 - 1)
```
The generated measurements are sent to the server via HTTP Post:

```python
    # serialize to JSON
    s = json.dumps(measurement)
    # Send data the server by using HTTP POST
    response = requests.post("http://localhost:5000/newmeasurement", data = s)
```

### measserver.py

The Python Flask program measserver.py receives the measurements and passes them to an html page using socket.io. The initialization and startup procedures of the program are shown below:

```python
import json
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# List of measurements
measurements = []

...

if __name__ == '__main__':
    socketio.run(app)
```

The get_line function handles a page request to the root. The function opens the linechart.html page in the browser.

```python
# Show the measurements
@app.route('/')
def get_line():
    return render_template('linechart.html')
```
The new_meas function receives a message sent via HTTP POST to /newmeasurement. The json-formatted measurement in the message is deserialized. The data originally in the dictionary (time, x, y and z) is converted to list format, since Google Charts requires the data in list format.

The new measurement is placed at the top of the measurements list (which is a list of lists) so that the newest measurement appears first in the table on the html page. The whole list of measurements is serialized and sent to the browser using the socketio.emit function.

```python
# Receive the measurements sent by HTTP POST
@app.route('/newmeasurement', methods=['POST'])
def new_meas():
    # read the measurement and deserialize it from JSON to object
    m = request.get_json(force=True)
    # convert the meaurement to suitable form of Google chart (dictionary -> list)
    mg = [m['time'], m['x'], m['y'], m['z']]
    # add measurement to the beginning of the list
    measurements.insert(0, mg)
    # serialize the list to JSON
    s = json.dumps(measurements)
    # broadcast the list to the clients by using socket.io
    socketio.emit('my_response', {'result': s})
    # return the measurement
    return json.dumps(m, indent=True)
```
### linechart.html

The linechart.html page is in the templates folder. The browser program receives the socketio messages and displays the measurements in linecharts and tables.

The structure of the page is shown below:

```html
<html>
    <head>
      <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
      <script type="text/javascript" src="//code.jquery.com/jquery-1.4.2.min.js"></script>
      <script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/socket.io/4.4.0/socket.io.min.js"></script>
      <script type="text/javascript" charset="utf-8"></script>         
      <script type="text/javascript">
      ...
      </script>
    </head>
    <body>
      <div id="curve_chart" style="width: 1000px; height: 500px"></div>
      <div id="table_div" style="width: 1000px; height: 500px"></div>
    </body>
  </html>
```
The line chart is displayed in the div element curve_chart and the table in the div element table_div.

The initialization of Google Chart and the reception of the socketio message is shown below:

```javascript
        google.charts.load('current', {'packages':['corechart', 'table']});
        google.charts.setOnLoadCallback(init);

        function init() {
          var socket = io();
          socket.on('my_response', function (data) {
            var s = JSON.parse(data.result);
            console.log(s)
            drawChart(s)
            drawTable(s)
          })
        }
```

The received socketio message contains a list of measurements. One row of measurements is also in the form of a list (time, x, y, z). When the socketio message is received, it is deserialized and the converted data is passed to drawChart() and drawTable().

The drawChart function draws a line chart in the div element curve_chart:

```javascript
        function drawChart(s) {
          var data = new google.visualization.DataTable();
            data.addColumn('number', 'time');
            data.addColumn('number', 'x');
            data.addColumn('number', 'y');
            data.addColumn('number', 'z');
            data.addRows(s);
  
          var options = {
            title: 'Indoor positioning system data',
            curveType: 'function',
            legend: { position: 'bottom' }
          };
  
          var chart = new google.visualization.LineChart(document.getElementById('curve_chart'));
  
          chart.draw(data, options);
        }
```

The drawTable function draws a table to the div element table_div:

```javascript
        // https://developers.google.com/chart/interactive/docs/gallery/table 
        function drawTable(s) {
          var data = new google.visualization.DataTable();
          data.addColumn('number', 'time');
          data.addColumn('number', 'x');
          data.addColumn('number', 'y');
          data.addColumn('number', 'z');
          data.addRows(s);
  
          var table = new google.visualization.Table(document.getElementById('table_div'));
  
          table.draw(data, {showRowNumber: false, width: '100%'});
        }
```

## Installing libraries and running programs

To run the programs you need to install the libraries Flask, Flask-SocketIO and requests:

```
pip install requests
pip install Flask
pip install Flask-SocketIO 
```

First, run the server program measserver.py (py measserver.py).

Then open the localhost:5000 page in your browser.

Then open a new terminal and start the program that generates the measurement data, either datageneratorclient.py.



