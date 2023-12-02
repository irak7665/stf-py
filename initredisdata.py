# -*- coding: utf-8 -*-
from flask import json

import globals_


def init_redis_data(serial):
    try:
        if globals_.r.hget("contact_list", serial) is None:
            globals_.r.hset("contact_list", serial, json.dumps([]))

        if globals_.r.get("add_contact_flag" + serial) is None:
            globals_.r.set("add_contact_flag" + serial, False)
        if globals_.r.hget("stranger_phone_list", serial) is None:
            globals_.r.hset("stranger_phone_list", serial, json.dumps(["123456789", "987654321"]))

        if globals_.r.get("init_global_message_list") is None:
            globals_.r.set("init_global_message_list", json.dumps([]))

    except Exception as e:
        raise Exception("init_redis_data error:", e)


def set_contact(serial, contact):
    globals_.r.hset("contact_list", serial, contact)


def set_stranger(serial, stranger):
    globals_.r.hset("stranger_phone_list", serial, stranger)


def get_stranger(serial):
    return globals_.r.hget("stranger_phone_list", serial)


def system_settings(data):
    globals_.r.hset("device_system_setting", "data", json.dumps({"interval": data.get('interval'),
                                                                 "pagesize": data.get('pagesize'),
                                                                 "init_message": data.get('init_message'),
                                                                 "loop_message_time": data.get('loop_message_time'),
                                                                 "wait_message_time": data.get('wait_message_time'),
                                                                 "add_contact_flag": data.get("add_contact_flag")}))


def device_settings(data):
    globals_.r.hset("device_system_setting", data.get('serial'), json.dumps({"interval": data.get('interval'),
                                                                             "pagesize": data.get('pagesize'),
                                                                             "init_message": data.get('init_message'),
                                                                             "loop_message_time": data.get(
                                                                                 'loop_message_time'),
                                                                             "wait_message_time": data.get(
                                                                                 'wait_message_time'),
                                                                             "add_contact_flag": data.get(
                                                                                 "add_contact_flag")}))
