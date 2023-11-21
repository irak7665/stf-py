import json

import requests
from flask import Flask, jsonify, request
import threading

import globals_
from chatapps.whatsapp import whatsapp
from initredisdata import init_redis_data
from services.deviceSet import setDeviceStatus
from services.send_message_phone import send_message_from_phone

app = Flask(__name__)


def response_json(status='ok', msg='', data='', code=200):
    return {'code': code, 'status': status, 'msg': msg, 'data': data}


@app.route('/get_devices', methods=['GET'])
def devices():
    t = threading.Thread(target=get_devices)
    t.start()
    return jsonify({'status': 'ok'})


# 返回设备对聊状态
@app.route('/get_device_status', methods=['POST'])
def get_device_status():
    serial = request.json.get('serial')
    status = int(globals_.r.hget("device_status", serial) or 0)
    return jsonify({'status': 'ok', 'data': status})


# 设置设备对聊状态为暂停
@app.route('/pause', methods=['POST'])
def pause():
    try:
        serial = request.json.get('serial')
        setDeviceStatus(serial, 2)
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)})


# 设置设备对聊状态为停止
@app.route('/stop', methods=['POST'])
def stop():
    try:
        serial = request.json.get('serial')
        setDeviceStatus(serial, 1)
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)})


# 设置设备对聊状态为运行
@app.route('/start_send_message', methods=['POST'])
def start_send_message():
    try:
        serial = request.json.get('serial')
        device_status = int(globals_.r.hget("device_status", serial) or 1)
        # 获取聊天对象
        contact = json.loads(globals_.r.hget("device_system_setting", serial)).encode("utf-8")['contact']
        data = {'rec': contact}

        # 如果该设备处于停止或者暂停状态，则设置为运行状态，并且启动运行线程
        if device_status == 1 or device_status == 2:
            setDeviceStatus(serial, 0)
            t = threading.Thread(target=send_message_from_phone, args=(data, serial,))
            t.start()
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)})


@app.route('/set_contact', methods=['POST'])
def set_contact():
    serial = request.json.get('serial')
    contact = request.json.get('contact')
    init_redis_data(serial)
    system_setting = json.loads(globals_.r.hget("device_system_setting", serial).encode("utf-8"))
    system_setting['contact'] = contact
    globals_.r.hset("device_system_setting", serial, json.dumps(system_setting))
    return jsonify({'status': 'ok'})


def get_devices():
    apiurl = 'http://192.168.1.102:7100/api/v1/devices'
    access_token = 'd8e1034635724eb68eacd8b25667b4b8cdf6d022af0c42b5be970a2d18fff4cf'

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    res = requests.get(apiurl, headers=headers)
    print(res.json())


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True, port=5000)
