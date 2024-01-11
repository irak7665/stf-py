import json

import redis
import requests

# import rethinkdb
# r = rethinkdb.RethinkDB()
# conn = r.connect('localhost', 28015).repl()
# res = r.db('stf').table('users').run(conn)
# for item in res:
#     print(item)
# import socketio

# sio = socketio.Client()
# try:
#     sio.connect("http://192.168.1.102:7170")
#     # sio.emit('device.note')
# except Exception as e:
#     print(str(e))
#     print("error:")
# def event_handler(msg):
#     print('Handler', msg)
#
# client = redis.StrictRedis(host='127.0.0.1', port=6379, db=1, decode_responses=True)
# pubsub = client.pubsub()
# pubsub.subscribe(**{'my-channel': event_handler})
#
# print('Starting message loop')
# while True:
#     message = pubsub.get_message()
#     if message and message['type'] == 'message':
#         event_handler(message['data'])
access_token = 'a3490fb6edca41948934325e2a3f9261b9cc858b4c4e4409bf118a572f068fbd'
headers = {
    'Authorization': f"Bearer {access_token}"
}
res = requests.get('http://192.168.1.102:7100/api/v1/devices/E6EYFQ5SBIMBHQUS', headers=headers)
data = json.loads(res.text)
print(data)
print(data['device']['runningState'])
