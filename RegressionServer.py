from flask import Flask, request
import flask
import requests
import json
import urllib.request
import numpy as np
from scipy import linalg

global AverageError
global p

AverageError = 0
p = 0

app = Flask(__name__)

@app.route("/", methods=['GET'])
def get_funct():
    print("this si a get request")
    r = request.referrer[:-1]
    headers = {'Content-Type': 'application/json'}
    resp = requests.get(r, headers = headers, stream=True)

    if (resp.status_code != 200):
        print("Request failed with status code:", resp.status_code)
    print(str(p) + "  " + str(AverageError))
    response = flask.jsonify({"Constants": p, "Error": AverageError })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/", methods=['POST'])

def index():
    print("tis is a post request")
    r = request.referrer[:-1]
    print(r)
    co_ords = []
    data = ''

    try:
        #data = json.loads(data)
        data = json.loads(request.data.decode('UTF-8'))
        co_ords = data['data']
        xpower = int(data['power'])
        print(co_ords)
        print(xpower)
        #print("bruh")
    except json.JSONDecodeError:
        print("Failed to parse data as JSON")
    
    x = []
    y = []
    for a in co_ords:
        print(a['x'])
        x.append(float(a['x']))
        y.append(float(a['y']))
        print(str(a['x']) + " " + str(a['y']))
    
    if (len(x)>0):
        AverageError,p = equationfinder(x,y,xpower)   #xpower
    else:
        print("no data")

    headers = {'Content-Type': 'application/json'}
    resp = requests.get(r, headers = headers, stream=True)

    if (resp.status_code != 200):
        print("Request failed with status code:", resp.status_code)

    response = flask.jsonify({"Constants": p, "Error": AverageError })
    response.headers.add('Access-Control-Allow-Origin', '*')

    print(str(p) + "  " + str(AverageError))

    return response

def equationfinder(x,y, xpower):
    arr = []
    yarr = []
    rp = xpower * 2
    for h in range(0,rp +1):
        s = 0
        arr.append([])
        arr[h].append([])
        arr[h][0].append(h)
        arr[h].append([])
        for n in range(0,len(x)):     
            s = s + ((x[n]**h))
        arr[h][1].append(s)

    for h in range(0,xpower +1):
        s = 0
        yarr.append([])
        yarr[h].append([])
        yarr[h][0].append(h)
        yarr[h].append([])
        for n in range(0,len(x)):     
            s = s + ((x[n]**h) * y[n])
          
        yarr[h][1].append(s)
    g = []

    for e in range(0, xpower + 1):
        g.append([])
        for z in range(0, xpower + 1):
           g[e].extend(arr[e+z][1])

    u = np.array(g,dtype='float')
    #if linalg.det(u) == 0:
    #    AverageError = 0
    #    grad = (y[1]-y[0])/(x[1]-x[0])
    #    p = [y[0], grad]
    #    return AverageError, p
    inv = np.linalg.inv(u)

    b = []
    for f in range(0, len(yarr)):
        b.append([])
        b[f].extend(yarr[f][1])
    b = np.array(b)
    p = np.matmul(inv, b)
    print(p)
    valx = []
    valy = []
    start = min(x)-1
    stop = max(x) +1
    step = 0.01
    while start < stop:
        start = start + step
        start = round(start,2)
        valx.append(start)

    for w in range(0, len(valx)):
        d = 0
        for j in range(0, xpower + 1):
            d = d + (p[j] * (valx[w]**j))
        valy.extend(d)

    error = 0
    for k in range(0, len(x)):   
       for q in range(0, len(valx)):
           if valx[q] == x[k]:
               error = error + abs(valy[q] - y[k])

    AverageError = error/len(x)
    print(AverageError)
    return AverageError,p.tolist() 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)



