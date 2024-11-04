import json
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Lista mittauksia varten
measurements = []

# Näytä mittaukset Google Chart -kaavion avulla
@app.route('/')
def get_line():
    return render_template('linechart.html')

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

if __name__ == '__main__':
    socketio.run(app)
   