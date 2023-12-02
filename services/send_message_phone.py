# -*- coding: utf-8 -*-
import json
import threading
import time
from datetime import datetime, timedelta
from globals_ import logger
import globals_
from chatapps.whatsapp import whatsapp


def send_message_from_phone(data, device_id_):
    device_id = device_id_
    system_setting = json.loads(globals_.r.hget("device_system_setting","data").encode("utf-8"))
    # 定义打招呼时间间隔 minute
    interval_ = int(system_setting['interval'] or 2)
    interval = timedelta(minutes=interval_)

    # 定义每次添加联系人的数量
    pagesize_ = int(system_setting['pagesize'] or 1)
    pagesize = pagesize_

    # 定义打招呼的内容
    init_message = system_setting['init_message'] or "Hello"

    # 定义每次添加联系人列表
    try:
        contract_list = json.loads(globals_.r.hget('stranger_phone_list', device_id)) or None
    except Exception as e:
        contract_list = []
        logger.error("contract_list error:{}"+str(e))

    # 是否在间隔一定时间后添加联系人开关
    add_contract_flag__ = globals_.r.hget("device_system_setting", device_id)
#     add_contract_flag_ = globals_.r.get['add_contact_flag'+device_id] or False
    add_contract_flag_ = False
    try:
        message_list = json.loads(globals_.r.get('init_global_message_list'))
    except Exception as e:
        message_list = ['你好sam哥，昨天和anne說好了，你什麼時候可以幫忙辦理好這個事情呀？', 'Hello~麻煩把你的車移一下好嘛？你佔用了我們公司的車位啦']
        logger.error("message_list error:{}"+str(e))

    if add_contract_flag_ is True:
        add_contract_flag = True
    else:
        add_contract_flag = False

    # 循环发消息的时间周期
    loop_message_time = int(globals_.r.get("loop_message_time") or 3)

    start_time = datetime.now()
    # end_time 3小时以后
    end_time = datetime.now() + timedelta(hours=loop_message_time)
    whatsapp_instance = whatsapp(device_id)
    index = int(globals_.r.get("index_tmp"+device_id) or 0)
    break_flag = False
    # 设置该设备正在运行发送消息线程
    globals_.r.hset("device_status", device_id, 0)

    # 暂停和恢复
    pause_event = threading.Event()
    resume_event = threading.Event()
    while datetime.now() <= end_time and break_flag is False:
        print("running...",device_id)
        stop = globals_.dbapi_instance.getRunningState(device_id)
        print("stop:", stop)
        if stop == 3:
            break
        if stop == 2: # 暂停
            pause_event.set()
        if stop ==0:
            pause_event.clear()
        if pause_event.is_set(): # 暂停
            resume_event.wait() # 阻塞
            resume_event.clear() # 清除
            pause_event.clear() # 清除

        if add_contract_flag:
            if datetime.now() - start_time >= interval:
                # 每隔interval分钟，添加pagesize个联系人
                add_contact_and_send_message(index, pagesize, contract_list, whatsapp_instance, init_message)
                index += pagesize
                if index >= len(contract_list):
                    index = 0
                globals_.r.set("index_tmp"+device_id, index)

                start_time = datetime.now()
        try:
            # 发送消息
            print(message_list)
            for message_item in message_list:
                stop = globals_.dbapi_instance.getRunningState(device_id)
                if stop == 3:
                    break
                if stop == 2:  # 暂停
                    pause_event.set()
                if stop == 0:
                    pause_event.clear()
                if pause_event.is_set():  # 暂停
                    resume_event.wait()  # 阻塞
                    resume_event.clear()  # 清除
                    pause_event.clear()  # 清除
                print("message_item:",message_item)
                whatsapp_instance.get_nickname()
                if whatsapp_instance.find_new_contact(data['rec']):
                    print("find_new_contact")
                    whatsapp_instance.input_message_click_send(message_item)
                else:
                    print("not find_new_contact")
            # whatsapp_instance.jump_to_main()
        except Exception as e:
            if str(e) == "device_not_found":
                print("设备离线")
                break_flag = True
                break
            print("send message error:{}".format(e))
    globals_.r.set("index_tmp"+device_id, 0)
    globals_.dbapi_instance.stop(device_id)


def add_contact_and_send_message(index, pagesize, contract_list, whatsapp_instance, init_message):
    """

    :param index:记录当前添加联系人的索引
    :param pagesize: 每次添加联系人的数量
    :param contract_list: 全部联系人列表
    :param whatsapp_instance: whatsapp实例
    :return:
    """
    whatsapp_instance.restart_whatsapp()
    end_index = pagesize + index
    if pagesize + index >= len(contract_list):
        end_index = len(contract_list)
    for item_contract in contract_list[index:end_index]:
        time.sleep(2)
        contract_item = item_contract
        # whatsapp_instance.add_contract(contract_item['country_code'], contract_item['contract'],
        #                                init_message)
        if whatsapp_instance.find_new_contact(contract_item['contract']):
            whatsapp_instance.input_message_click_send(init_message)
        else:
            print("not find_new_contact")





