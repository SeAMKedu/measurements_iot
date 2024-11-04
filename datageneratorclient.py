import requests    
import json   
import math   
import time  
import random 

t = 0
while t < 10:
    # generate a measurement
    measurement = { }
    measurement['time'] = t
    measurement['x'] = 5 * math.cos(t) + (random.random() * 2 - 1)
    measurement['y'] = 6 * math.sin(t) + (random.random() * 2 - 1)
    measurement['z'] = (random.random() * 2 - 1)

    # serialize the measurement to JSON format
    s = json.dumps(measurement)
    # send the data to the server by HTTP POST
    response = requests.post("http://localhost:5000/uusimittaus", data = s)

    print(s)
    time.sleep(0.5)

    t += 0.1

