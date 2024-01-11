# -*- coding: utf-8 -*-
import json
import os

from flask import Flask, jsonify, request
import globals_
from initredisdata import system_settings, set_contact, set_stranger, device_settings
from services.message_sender import MessageSender
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
thread_dict = {}


def response_json(status='ok', msg='', data='', code=200):
    return {'code': code, 'status': status, 'msg': msg, 'data': data}


# 设置设备对聊状态为暂停
@app.route('/pause', methods=['POST'])
def pause():
    try:
        serial = request.json.get('serial')
        thread_dict[serial].pause()
        globals_.dbapi_instance.setRunningTips(serial, 'paused')
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)})


@app.route('/installatx', methods=['POST'])
def handle_install_atx():
    try:
        serial = request.json.get('serial')
        cmd = f"python -m uiautomator2 init -s {serial}"
        info = os.system(cmd)
        if "Successfully" in info:
            return jsonify({'status': 'ok'})
        else:
            return jsonify({'status': 'error', 'msg': str(info)})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(info)})


# 设置设备对聊状态为停止
@app.route('/stop', methods=['POST'])
def stop():
    try:
        serial = request.json.get('serial')
        if serial in thread_dict:
            del thread_dict[serial]
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)})


# 设置设备对聊状态为运行
@app.route('/start_send_message', methods=['POST'])
def start_send_message():
    try:
        serial = request.json.get('serial')
        device_status = globals_.dbapi_instance.getRunningState(serial)

        # 获取聊天对象
        contact = globals_.r.hget('contact_list', serial)
        data = {'rec': contact}

        if serial not in thread_dict:
            # 如果线程不存在，创建并存储它
            thread_dict[serial] = MessageSender(data, serial)

        if device_status == 1 or device_status == 3:
            # 如果设备状态为 1 或 3，启动线程
            if not thread_dict[serial].is_alive():
                thread_dict[serial].start()

        elif device_status == 2:
            # 如果设备状态为 2，恢复线程
            thread_dict[serial].resume()

        return jsonify({'status': 'ok'})

    except Exception as e:
        print(str(e))
        serial = request.json.get('serial')
        globals_.dbapi_instance.stop(serial)
        return jsonify({'status': 'error', 'msg': str(e)})


@app.route('/set_contact', methods=['POST'])
def set_contacts():
    serial = request.json.get('serial')
    contact = request.json.get('contact')
    set_contact(serial, contact)
    return jsonify({'status': 'ok'})


@app.route('/get_contact', methods=['POST'])
def get_contacts():
    serial = request.json.get('serial')
    contact = globals_.r.hget('contact_list', serial)
    return jsonify({'status': 'ok', 'data': contact})


@app.route('/set_stranger_v1', methods=['POST'])
def set_strangers():
    serial = request.json.get('serial')
    stranger = request.json.get('contacts')
    set_stranger(serial, stranger)
    return jsonify({'status': 'ok'})


@app.route('/get_stranger', methods=['POST'])
def get_strangers():
    serial = request.json.get('serial')
    contact = globals_.r.hget('stranger_phone_list', serial)
    print(contact)
    return jsonify({'status': 'ok', 'data': contact})


@app.route('/system_setting', methods=['POST'])
def system_setting():
    interval = request.json.get('interval')
    init_message = request.json.get('init_message')
    loop_message_time = request.json.get('loop_message_time')
    pagesize = request.json.get('pagesize')
    wait_message_time = request.json.get('wait_message_time')
    add_contact_flag = request.json.get('add_contact_flag')
    if add_contact_flag is None:
        add_contact_flag = False
    data = {'interval': interval, 'init_message': init_message, 'loop_message_time': loop_message_time,
            'pagesize': pagesize, 'wait_message_time': wait_message_time,'add_contact_flag': add_contact_flag}
    system_settings(data)
    return jsonify({'status': 'ok'})

@app.route('/init_message_list', methods=['POST'])
def init_message_list():
    init_global_message_list = request.json.get('init_message_list')
    globals_.r.set('init_global_message_list',init_global_message_list)
    return jsonify({'status': 'ok', 'data': init_global_message_list})

@app.route('/get_init_message_list', methods=['GET'])
def get_init_message_list():
    init_message_list = globals_.r.get('init_global_message_list')
    return jsonify({'status':'ok','data':init_message_list})

@app.route('/get_setting', methods=['GET'])
def get_setting():
    data = globals_.r.hget("device_system_setting", "data")
    return jsonify({'status': 'ok', "data": json.loads(data)})

@app.route('/device_setting', methods=['POST'])
def device_setting():
    serial = request.json.get('serial')
    print('serial:',serial)
    interval = request.json.get('interval')
    init_message = request.json.get('init_message')
    loop_message_time = request.json.get('loop_message_time')
    pagesize = request.json.get('pagesize')
    wait_message_time = request.json.get('wait_message_time')
    add_contact_flag = request.json.get('add_contact_flag')
    if add_contact_flag is None:
        add_contact_flag = False
    data = {'serial': serial,'interval': interval, 'init_message': init_message, 'loop_message_time': loop_message_time,
            'pagesize': pagesize, 'wait_message_time': wait_message_time, 'add_contact_flag': add_contact_flag}
    device_settings(data)
    return jsonify({'status': 'ok'})

@app.route('/get_device_setting', methods=['POST'])
def get_device_setting():
    serial = request.json.get('serial')
    print("get_device_setting_serial:",serial)
    data = globals_.r.hget("device_system_setting", serial)
    print("data:",data)
    return jsonify({'status': 'ok','data': json.loads(data)})




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True,  port=5000)
