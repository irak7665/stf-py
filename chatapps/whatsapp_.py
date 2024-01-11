# -*- coding: utf-8 -*-
import json
import os
import time

import uiautomator2 as u2

import globals_
from chatapps.IM import IM
from globals_ import logger


class whatsapp(IM):
    def __init__(self, device_id):
        """
        """
        self.device_id = device_id
        self.connect_device()

    def connect_device(self):
        """
        连接设备
        """
        try:
            # 检查 atx-agent 是否已安装
            result = os.popen(
                f'adb -s {self.device_id} shell pm list packages | grep "package:com.github.uiautomator"').read()
            if 'com.github.uiautomator' in result:
                # 卸载 atx-agent
                os.system(f'adb -s {self.device_id} uninstall com.github.uiautomator')
                print("已卸载旧的 atx-agent")
            else:
                print("未安装 atx-agent，无需卸载")
            self.d = u2.connect(self.device_id)
        except Exception as e:
            logger.error("连接设备失败:{}".format(str(e)))

    def start_whatsapp(self):
        try:
            self.d.app_stop("com.whatsapp")
            time.sleep(1)
            self.d.app_start("com.whatsapp", activity="com.whatsapp.HomeActivity")
            time.sleep(5)
        except Exception as e:
            self.notify_error_stop()
            print(str(e))

    # 检测静音
    def check_mute(self):
        try:
            if self.d(resourceId="android:id/action0", text="静音").exists:
                self.d(resourceId="android:id/action0", text="静音").click()
                time.sleep(1)
                self.d(text="总是").click()
                time.sleep(1)
                self.d(resourceId="android:id/button1").click()
            if self.d(resourceId="android:id/action0", text="靜音").exists:
                self.d(resourceId="android:id/action0", text="靜音").click()
                time.sleep(1)
                self.d(text="總是").click()
                time.sleep(1)
                self.d(resourceId="android:id/button1").click()
        except Exception as e:
            pass

    def find_contact(self, receiver):

        self.check_mute()

        receiver_ = "+" + str(receiver)
        try:
            print("self.d.current_app['activity']:",self.d.current_app()['activity'])
            if 'Conversation' in str(self.d.current_app()['activity']):
                print("Conversation in activity retun true...")
            # if self.d.current_app()['activity'] == "com.whatsapp.Conversation":
                return True
                # if self.d(resourceId="com.whatsapp:id/conversation_contact_name").get_text().strip().replace(" ",
                #                                                                                              "") == receiver_:
                #     return True
                # else:
                #     self.jump_to_main()
            else:
                self.start_whatsapp()
                if not self.d(resourceId="com.whatsapp:id/tab").exists:
                    globals_.dbapi_instance.setRunningTips(self.device_id, 'error')
                    return 'bad'
                # 进入主界面点击“对话”的tab
                if self.d(resourceId="com.whatsapp:id/tab",text="對話").exists:
                    self.d(resourceId="com.whatsapp:id/tab",text="對話").click()
                elif self.d(resourceId="com.whatsapp:id/tab", text="对话").exists:
                    self.d(resourceId="com.whatsapp:id/tab", text="对话").click()
                time.sleep(1)
                # 点击右下角的“新建信息”按钮
                self.d(resourceId="com.whatsapp:id/fab").click()
                time.sleep(1)
                # 点击“查找联系人”按钮
                if self.d(resourceId="com.whatsapp:id/menuitem_search").exists:
                    self.d(resourceId="com.whatsapp:id/menuitem_search").click()
                    time.sleep(1)
                    # 输入联系人名称
                    self.d(focused=True).set_text(receiver)
                    time.sleep(1)
                    # click contact
                    self.d(resourceId="com.whatsapp:id/contactpicker_row_name").click()
                    time.sleep(1)
                    return True
                else:
                    globals_.dbapi_instance.stop(self.device_id)
                    globals_.dbapi_instance.setRunningTips(self.device_id,'add at least one conact first')
                    return False

        except Exception as e:
            logger.error("查找陌生联系人失败:{}".format(str(e)))
            return False

    def back_up(self):
        time.sleep(2)
        self.d(resourceId="com.whatsapp:id/whatsapp_toolbar_home").click()

    def jump_to_main(self):
        self.d(resourceId="com.whatsapp:id/whatsapp_toolbar_home").click()
        time.sleep(1)

    def exist_element(self,rec):
        if not self.d(resourceId="com.whatsapp:id/conversation_entry_action_button").exists:
            self.find_contact(rec)

    def input_message_click_send(self, message, rec):
        """
        """
        if 'Conversation' not in str(self.d.current_app()['activity']):
        # if self.d.current_app()['activity'] != "com.whatsapp.Conversation" and self.d.current_app()['activity'] != ".Conversation":
            if self.find_contact(rec) == 'bad':
                print("bad activity")
                return 'bad'
        else:
            self.exist_element(rec)
            # 输入消息
            # self.d.send_keys(message)
            if message != '':
                self.d(focused=True).set_text(message)
                # 点击发送
                time.sleep(3)
                self.d(resourceId="com.whatsapp:id/conversation_entry_action_button").click()
        return True

    def notify_error_stop(self):
        globals_.dbapi_instance.stop(self.device_id)
