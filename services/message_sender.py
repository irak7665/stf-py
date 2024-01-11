import random
import threading
import time
from datetime import timedelta, datetime

from flask import json

import globals_
from chatapps.whatsapp_ import whatsapp


class MessageSender(threading.Thread):
    def __init__(self, data, serial):
        super().__init__()
        self.data = data
        self.serial = serial
        self.pause_event = threading.Event()
        self.pause_event.set()  # 默认设置为运行状态
        self.logger = globals_.logger

    def run(self):

        device_id = self.serial

        globals_.dbapi_instance.setRunningTips(device_id,'already running')
        system_setting = {'interval': 20, 'pagesite': 1, 'init_message': 'Hello', 'loop_message_time': 3,
                          'wait_message_time': '1-60','add_contact_flag': False}
        try:
            system_setting = json.loads(globals_.r.hget("device_system_setting", "data").encode("utf-8"))
        except:
            pass

        if globals_.r.hget("device_system_setting", device_id) is not None:
            device_setting = json.loads(globals_.r.hget("device_system_setting", device_id))
        else:
            device_setting = False

        if device_setting is not False:
            if device_setting['interval'] != '':
                interval_ = int(device_setting['interval'])
            else:
                interval_ = int(system_setting['interval'])
            if device_setting['pagesize'] != '':
                pagesize_ = int(device_setting['pagesize'])
            else:
                pagesize_ = int(system_setting['pagesize'])
            if device_setting['loop_message_time'] != '':
                loop_message_time_ = int(device_setting['loop_message_time'])
            else:
                loop_message_time_ = int(system_setting['loop_message_time'])
            if device_setting['init_message'] != '':
                init_message_ = device_setting['init_message']
            else:
                init_message_ = system_setting['init_message']
            if device_setting['wait_message_time'] != '':
                wait_message_time_ = device_setting['wait_message_time']
            else:
                wait_message_time_ = system_setting ['wait_message_time']
            if device_setting['add_contact_flag'] != '':
                add_contact_flag_ = device_setting['add_contact_flag']
            else:
                add_contact_flag_ = system_setting['add_contact_flag']

        else:
            interval_ = int(system_setting['interval'])
            pagesize_ = int(system_setting['pagesize'])
            loop_message_time_ = int(system_setting['loop_message_time'])
            init_message_ = system_setting['init_message']
            wait_message_time_ = system_setting['wait_message_time']
            add_contact_flag_ = system_setting['add_contact_flag']

        # 定义打招呼时间间隔 minute
        interval = timedelta(minutes=interval_)

        # 定义每次添加联系人的数量
        pagesize = pagesize_

        # 定义打招呼的内容
        init_message = init_message_

        # wait_message_time
        wait_message_time = wait_message_time_
        try:
            wait_message_time_start = int(wait_message_time.split('-')[0])
            wait_message_time_end = int(wait_message_time.split('-')[1])
        except:
            wait_message_time_start = 1
            wait_message_time_end = 60

        # 定义每次添加联系人列表
        try:
            if globals_.r.hget('stranger_phone_list', device_id) != '':
                contract_list = globals_.r.hget('stranger_phone_list', device_id).split('\n')
        except Exception as e:
            contract_list = []
            self.logger.error("contract_list error:{}" + str(e))

        # 是否在间隔一定时间后添加联系人开关
        add_contact_flag = add_contact_flag_
        try:
            if globals_.r.get('init_global_message_list') != '':
                message_list = globals_.r.get('init_global_message_list').split('\n')
            else:
                message_list = ['你好sam哥，昨天和anne說好了，你什麼時候可以幫忙辦理好這個事情呀？',
                            'Hello~麻煩把你的車移一下好嘛？你佔用了我們公司的車位啦']
        except Exception as e:
            message_list = ['你好sam哥，昨天和anne說好了，你什麼時候可以幫忙辦理好這個事情呀？',
                            'Hello~麻煩把你的車移一下好嘛？你佔用了我們公司的車位啦']

        # 循环发消息的时间周期
        loop_message_time = loop_message_time_

        start_time = datetime.now()
        # end_time 3小时以后
        end_time = datetime.now() + timedelta(hours=loop_message_time)
        whatsapp_instance = whatsapp(device_id)
        index = int(globals_.r.get("index_tmp" + device_id) or 0)
        break_flag = False
        # 设置该设备正在运行发送消息线程
        globals_.r.hset("device_status", device_id, 0)
        whatsapp_instance.start_whatsapp()
        input_message_click_send_result = ''
        find_contact_result = whatsapp_instance.find_contact(self.data['rec'])

        while datetime.now() <= end_time and break_flag is False:
            self.pause_event.wait()
            print("running...", device_id)
            stop = globals_.dbapi_instance.getRunningState(device_id)
            print("stop:", stop)
            if stop == 1 or find_contact_result == 'bad':
                break
            if add_contact_flag:
                if datetime.now() - start_time >= interval:
                    # 每隔interval分钟，添加pagesize个联系人
                    if len(contract_list) > 0:
                        self.add_contact_and_send_message(index, pagesize, contract_list, whatsapp_instance, init_message)
                        index += pagesize
                        if index >= len(contract_list):
                            index = 0
                        globals_.r.set("index_tmp" + device_id, index)
                        start_time = datetime.now()
            try:
                # 发送消息
                for message_item in message_list:
                    self.pause_event.wait()
                    stop = globals_.dbapi_instance.getRunningState(device_id)
                    if stop == 1 or find_contact_result == 'bad':
                        break_flag = True
                        break
                    input_message_click_send_result = whatsapp_instance.input_message_click_send(message_item,self.data['rec'])
                    time.sleep(random.randint(wait_message_time_start, wait_message_time_end))

            except Exception as e:
                if str(e) == "device_not_found":
                    print("设备离线")
                    break_flag = True
                    break
                print("send message error:{}".format(e))
        globals_.dbapi_instance.stop(device_id)

        if find_contact_result == 'bad' or input_message_click_send_result =='bad':
            globals_.dbapi_instance.setRunningTips(device_id, 'error')
        else:
            globals_.dbapi_instance.setRunningTips(device_id, 'stoped')

    def add_contact_and_send_message(self, index, pagesize, contract_list, whatsapp_instance, init_message):
        """

        :param init_message:
        :param index:记录当前添加联系人的索引
        :param pagesize: 每次添加联系人的数量
        :param contract_list: 全部联系人列表
        :param whatsapp_instance: whatsapp实例
        :return:
        """
        whatsapp_instance.start_whatsapp()
        end_index = pagesize + index
        if pagesize + index >= len(contract_list):
            end_index = len(contract_list)
        for item_contract in contract_list[index:end_index]:
            self.pause_event.wait()
            time.sleep(2)
            contract_item = item_contract
            if whatsapp_instance.find_contact(contract_item):
                whatsapp_instance.input_message_click_send(init_message, self.data['rec'])
                whatsapp_instance.back_up()
            else:
                print("not find_new_contact")

    def pause(self):
        self.pause_event.clear()

    def resume(self):
        self.pause_event.set()
