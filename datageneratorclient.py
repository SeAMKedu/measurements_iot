import requests    
import json   
import math   
import time  
import random 

t = 0
while t < 10:
    # import random 
    measurement = { }
    measurement['time'] = t
    measurement['x'] = 5 * math.cos(t) + (random.random() * 2 - 1)
    measurement['y'] = 6 * math.sin(t) + (random.random() * 2 - 1)
    measurement['z'] = (random.random() * 2 - 1)

    # muunna json-muotoon 
    s = json.dumps(measurement)
    # TODO: lähetä data HTTP Postilla serverille
    response = requests.post("http://localhost:5000/uusimittaus", data = s)

    print(s)
    time.sleep(0.5)

    t += 0.1

