import websocket
import json
import time
import numpy as np
"""
NOTES:
1 = open, 0 = closed servo placement
60 = open, 120 = closed on servo itself
S067 is move to 67
"""
DEBUG = True
BREATH_RANGE = [12, 17] #min, max breathing rate per minute, maps to totally open and totally closed.
PREV = [0, 0, 0] #start with history of "closed" to make them open it for demo.

def servo_move(breath):
    """breath is smoothbr, breathing rate, usually between 8 (low) and 15 (high)"""
    #cutoff the range to be within BREATH_RANGE
    if breath < BREATH_RANGE[0]:
        breath = BREATH_RANGE[0]
    elif breath > BREATH_RANGE[1]:
        breath = BREATH_RANGE[1]
    val = 1 - (breath - BREATH_RANGE[0])/(BREATH_RANGE[1] - BREATH_RANGE[0]) #normalize to 0-100.

    #average over previous 3 breaths, discarding oldest at top of stack.
    PREV.pop(0) #pop position zero off
    PREV.append(val) #add newest to end
    avg = np.mean(PREV)


def parse_message(message):
    """
    {
    "action":"event",
    "user_key":"deadbeefdeadbeef",
    "metadata":
        {
        "sensor_uuid":"DEADBEEF-DEAD-BEEF-DEAD-BEEFDEADBEEF",
        "sensor_name":"Spire B5",
        "category":"breath",
        "keys":["ts","smoothbr"],
        "count":1,
        "from":1405126548.04,
        "to":1405126548.04},
        "data":
            [
                {
                "ts":1405126548.04,
                "smoothbr":10.9009936619
                }
            ]
    }
    """
    msg = json.loads(message)
    if msg.has_key('data') and msg['data'][0].has_key('smoothbr'):
        br = msg['data'][0]['smoothbr']
        print('breathing is %s' %br)
        servo_move(br) #sends to function that will calibrate value from 0-100 and the call the servo fxn

def on_message(ws, message):
    print "message: ", message
    parse_message(message)

def on_error(ws, error):
    print "error: ", error

def on_close(ws):
    print "WebSocket connection closed."

def on_open(ws):
    s = {
        "action":"subscribe",
        "type": "user",
        "user_key":"932884c6ccc7a62b",
        "user_auth_hash":"83700a11827f4d1e0849",
        "event" : ["breath.smoothbr"]
        }
    json_data = json.dumps(s)
    ws.send(json_data)

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        "ws://dev.spire.io:8888/api/v1/deadbeefdeadbeef",
        on_message = on_message,
        on_error = on_error,
        on_close = on_close
    )
    ws.on_open = on_open
    ws.run_forever()
