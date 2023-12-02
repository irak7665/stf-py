import redis
import requests
import rethinkdb
from flask import json


# r = rethinkdb.RethinkDB()


class Dbapi():
    def __init__(self):
        # self.r = rethinkdb.RethinkDB()
        # self.conn = self.r.connect('127.0.0.1', 28015).repl()
        self.client = redis.StrictRedis(host='localhost', port=6379, db=1)
    def setRunningState_run(self, serial):
        data_ = {'serial': serial, 'runningState': 0}
        data = json.dumps(data_)

        self.client.publish('automationState', data)
    def setRunningTips(self, serial, tips):
        data_ = {'serial': serial, 'runningTips': tips}
        data = json.dumps(data_)
        self.client.publish('automationTips', data)


    def stop(self, serial):
        # update_query = self.r.db('stf').table('devices').filter(self.r.row['serial'] == serial).update(
        #     {'runningState': 1})
        # result = update_query.run(self.conn)
        # print(result)
        # self.close()
        data_ = {'serial': serial, 'runningState': 1}
        data = json.dumps(data_)
        self.client.publish('automationState', data)

    def getRunningState(self, serial):
        access_token = 'a3490fb6edca41948934325e2a3f9261b9cc858b4c4e4409bf118a572f068fbd'
        headers = {
            'Authorization': f"Bearer {access_token}"
        }
        res = requests.get('http://192.168.1.102:7100/api/v1/devices/'+serial, headers=headers)
        data = json.loads(res.text)
        running_state = data['device']['runningState']
        print("runningState:",running_state)
        return running_state

    # def close(self):
    #     self.conn.close()

# sf = Dbapi()
# sf.setRunningTips('K7J749TSLJKBJN4S','ss333s22')

