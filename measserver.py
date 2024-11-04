import json
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# List of measurements (this list can be replaced by a database)
measurements = []

# Show the measurements
@app.route('/')
def get_line():
    return render_template('linechart.html')

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

if __name__ == '__main__':
    socketio.run(app)
   
