from flask import json

import globals_


def init_redis_data(serial):
    try:
        if globals_.r.hget("contact_list", serial) is None:
            globals_.r.hset("contact_list", serial, json.dumps([]))

        if globals_.r.hget("device_system_setting", "data") is None:
            globals_.r.hset("device_system_setting", "data", json.dumps({"interval": 1, "pagesize": 1,
                                                                         "init_message": "hello",
                                                                         "loop_message_time": 3}))
        if globals_.r.get("add_contact_flag"+serial) is None:
            globals_.r.set("add_contact_flag"+serial, False)
        if globals_.r.hget("stranger_phone_list", serial) is None:
            globals_.r.hset("stranger_phone_list", serial, json.dumps(["123456789", "987654321"]))

        if globals_.r.get("init_global_message_list") is None:
            globals_.r.set("init_global_message_list", json.dumps([]))

    except Exception as e:
        raise Exception("init_redis_data error:", e)
