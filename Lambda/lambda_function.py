import os, sys, json
import urllib.request
import urllib.parse

LINE_TOKEN = os.environ["LINE_TOKEN"]
LINE_URL = os.environ["LINE_URL"]

def lambda_handler(event, context):
    print(event)
    data = json.loads(json.dumps(event))
    message = data["payload"]["state"]["variables"]
    print("Date::  %s " % data)
    
    method = "POST"
    headers = {"Authorization": "Bearer %s" % LINE_TOKEN}
    payload = {"message": message}
    try:
        payload = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(
            url=LINE_URL, data=payload, method=method, headers=headers)
        urllib.request.urlopen(req)
    except Exception as e:
        print ("Exception Error: ", e)
