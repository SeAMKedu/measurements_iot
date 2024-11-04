# Python Flask, Socket.io ja Google Charts
[![DOI](https://zenodo.org/badge/733807414.svg)](https://zenodo.org/doi/10.5281/zenodo.10409021)

Tässä esimerkissä näytetään, miten mittausdataa voidaan näyttää web-sovelluksessa Google Chartin avulla niin, että data päivittyy reaaliaikaisesti.

Ohjelma datageneratorclient.py (tai readdata.py) generoi simuloitua mittausdataa ja lähettää sen palvelinohjelmalle. Flaskilla toteutettu palvelinohjelma measserver.py vastaanottaa mittaukset ja välittää ne html-sivulle, jossa ne näytetään Google Chart -kaavioina. Palvelinohjelman ja html-sivun välisessä kommunikoinnissa käytetään socket.io:ta.

## Tiedostot

### datageneratorclient.py

Python-ohjelma datageneratorclient.py generoi simuloitua mittausdataa. Kuvitteellisen laitteen paikkakoordinaatit generoidaan trigonometristen funktioiden avulla:

```python
    measurement = { }
    measurement['time'] = t
    measurement['x'] = 5 * math.cos(t) + (random.random() * 2 - 1)
    measurement['y'] = 6 * math.sin(t) + (random.random() * 2 - 1)
    measurement['z'] = (random.random() * 2 - 1)
```
Generoidut mittaukset lähetetään palvelimelle HTTP Postin avulla:

```python
    # muunna json-muotoon 
    s = json.dumps(measurement)
    # TODO: lähetä data HTTP Postilla serverille
    response = requests.post("http://localhost:5000/uusimittaus", data = s)
```

Ohjelma  **readdata.py** toimii samaan tapaan kuin datageneratorclient.py. Sen sijaan, että se generoisi dataa simuloimalla, se lukee sisätilapaikannusjärjestelmän tuottamaa sijaintitietoa tiedostosta **data_2022_02_23.txt**.

### measserver.py

Python Flask-ohjelma measserver.py vastaanottaa mittaukset ja välittää ne html-sivulle socket.io:n avulla.

Ohjelman alustukset ja käynnistytoimenpiteet on esitetty alla:

```python
import json
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Lista mittauksia varten
measurements = []

...

if __name__ == '__main__':
    socketio.run(app)
```

Funktio get_line käsittelee juureen osoitetun sivupyynnön. Funktio avaa sivun linechart.html selaimessa.

```python
# Näytä mittaukset Google Chart -kaavion avulla
@app.route('/')
def get_line():
    return render_template('linechart.html')
```
Funktio new_meas ottaa vastaan HTTP POST:lla osoitteeseen /uusimittaus lähetetyn viestin. Viestissä oleva json-muotoinen mittaus deserialisoidaan. Alun perin sanakirjassa olleet tiedot (aika, x, y ja z) muunnetaan listamuotoon, sillä Google Charts vaatii tiedon listamuotoisena.

Uusi mittaus sijoitetaan measurements-listan alkuun (joka on siis lista listoja), että uusin mittaus näkyisi html-sivulla olevassa taulukossa ensimmäisenä. Koko measurements-lista sarjallistetaan ja lähetetään selaimelle socketio.emit-funktiolla.

```python
# Otetaan vastaan HTTP POSTilla lähetty mittaus ja laitetaan se listaan
@app.route('/uusimittaus', methods=['POST'])
def new_meas():
    # luetaan data viestistä ja deserialisoidaan JSON-data
    m = request.get_json(force=True)
    # muutetaan mittaus Google Chartille sopivaan muotoon (sanakirja -> lista)
    mg = [m['time'], m['x'], m['y'], m['z']]
    # laitetaan listamuotoinen mittaus taulukon alkuun
    measurements.insert(0, mg)
    # lähetetään koko lista socket.io:n avulla html-sivulle
    s = json.dumps(measurements)
    socketio.emit('my_response', {'result': s})
    # palautetaan vastaanotettu tieto
    return json.dumps(m, indent=True)
```
### linechart.html

Sivu linechart.html on templates-kansiossa. Selainohjelma ottaa vastaan socketio-viestejä ja näyttää niissä olevat mittaukset viivakaavioissa ja taulukossa.

Sivun rakenne on esitetty alla:

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
Viivakaavio näytetään div-elementissä curve_chart ja taulukko div-elemntissä table_div.

Google Chartin alustus ja socketio-viestin vastaanotto on esitetty alla:

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

Saapunut socketio-viesti sisältää listan mittauksia. Yksi mittausrivi on on myös listan muodossa (aika, x, y, z). Kun socketio-viesti on saapunut, se deserialisoidaan ja muunnettu tieto välitetään funktioille drawChart() ja drawTable().

Funktio drawChart piirtää viivakaavion div-elementtiin curve_chart:

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

Funktio drawTable tekee taulukon div-elementtiin table_div:

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

## Kirjastojen asennus ja ohjelmien ajaminen

Ohjelmien ajamiseksi täytyy asentaa kirjastot Flask, Flask-SocketIO ja requests:

```
pip install requests
pip install Flask
pip install Flask-SocketIO 
```

Käynnistä ensin palvelinohjelma measserver.py (py measserver.py).

Avaa sitten selaimesta sivu localhost:5000.

Avaa sitten uusi terminaali ja käynnistä mittausdataa tuottava ohjelma, joko datageneratorclient.py tai readdata.py



