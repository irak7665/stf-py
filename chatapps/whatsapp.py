# -*- coding: utf-8 -*-
import json
import time

import uiautomator2 as u2

from chatapps.IM import IM
from globals_ import logger


class whatsapp(IM):
    def __init__(self, device_id):
        """
        """
        self.device_id = device_id
        self.connect_device()
        self.info = self.d.info
        self.device_info = self.d.device_info

        print("self.info:",self.info)
        print("self.device_info:",self.d.device_info)

    def connect_device(self):
        """
        连接设备
        """
        try:
            self.d = u2.connect(self.device_id)
        except Exception as e:
            logger.error("连接设备失败:{}".format(str(e)))
    def get_model(self):
        """
        获取并返回设备型号
        异常返回Unknown
        """
        try:
            model = self.device_info['brand']+"-"+self.info['productName']
        except Exception as e:
            logger.error("获取设备型号失败:{}".format(str(e)))
            model = "Unknown"
        return model
    def get_system_version(self):
        """
        获取并返回系统版本
        异常返回Unknown
        """
        try:
            system_version = self.info['version']
        except Exception as e:
            logger.error("获取系统版本失败:{}".format(str(e)))
            system_version = "Unknown"
        return system_version
    def get_window_size(self):
        """
        获取并返回屏幕分辨率
        异常返回Unknown
        """
        try:
            window_size = str(self.info['displayWidth']) + "x" + str(self.info['displayHeight'])
        except Exception as e:
            logger.error("获取屏幕分辨率失败:{}".format(str(e)))
            window_size = "Unknown"
        return window_size

    def get_nickname(self):
        """
        获取并返回WhatsApp昵称
        异常返回Unknown
        """
        try:
            self.d.app_stop("com.whatsapp")
            time.sleep(1)
            self.d.app_start("com.whatsapp", activity="com.whatsapp.HomeActivity")
            time.sleep(5)
            self.d(resourceId="com.whatsapp:id/menuitem_overflow").click()
            time.sleep(2)
            self.d(resourceId="com.whatsapp:id/title", text="设置").click()
            time.sleep(2)
            nickname = self.d(resourceId="com.whatsapp:id/profile_info_name").get_text()  # TODO: 此处需要根据实际元素进行调整
            self.d(description="转到上一层级").click()
        except u2.UiObjectNotFoundError as e:
            logger.error("获取WhatsApp昵称失败:{}".format(str(e)))
            nickname = "Unknown"
        return nickname

    # 从聊天窗口跳转到主界面
    def jump_to_main(self):
        self.d(resourceId="com.whatsapp:id/whatsapp_toolbar_home").click()
        time.sleep(1)

    # 查找陌生联系人
    def find_new_contact(self, receiver):
        """
        查找陌生联系人
        """
        self.check_mute()
        receiver_ = "+" + str(receiver)
        try:
            if self.d.current_app()['activity'] == "com.whatsapp.Conversation":
                if self.d(resourceId="com.whatsapp:id/conversation_contact_name").get_text().strip().replace(" ","") == receiver_:
                    return True
                else:
                    self.jump_to_main()
            # 进入主界面点击“对话”的tab
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

                # 点击联系人
                # if self.d(resourceId="com.whatsapp:id/contactpicker_row_name").get_text().replace(" ","") == receiver_:
                if True:
                    self.d(resourceId="com.whatsapp:id/contactpicker_row_name").click()
                    time.sleep(1)
                    return True
                else:
                    return False
        except Exception as e:
            logger.error("查找陌生联系人失败:{}".format(str(e)))
            return False


    # 检测静音
    def check_mute(self):
        try:
            if self.d(resourceId="android:id/action0", text="静音").exists:
                self.d(resourceId="android:id/action0", text="静音").click()
                time.sleep(1)
                self.d(text="总是").click()
                time.sleep(1)
                self.d(resourceId="android:id/button1").click()
        except Exception as e:
            pass
    # 发送消息主方法
    def send_message(self, receiver, message):
        """
        发送成功返回True，否则返回False
        异常情况下抛出:send_message_error
        """
        try:
            # 如果当前页面是聊天页面，并且聊天对象是receiver
            if self.d.current_app()['activity'] == "com.whatsapp.Conversation":
                if self.d(resourceId="com.whatsapp:id/conversation_contact_name").get_text() == receiver:
                    time.sleep(2)
                    self.input_message_click_send(message)
                    return True

            # 如果是其他联系人聊天窗口，则回退到主页面
            time.sleep(2)
            if self.d(resourceId="com.whatsapp:id/whatsapp_toolbar_home").exists:
                self.d(resourceId="com.whatsapp:id/whatsapp_toolbar_home").click()
                time.sleep(1)
            # 如果是搜索页面，则回退到主页面
            if self.d(description="返回").exists:
                self.d(description="返回").click()
                time.sleep(1)
            # 再次查找联系人
            if self.find_contact(receiver):
                self.input_message_click_send(message)
                return True
            else:
                # 否则重启WhatsApp
                self.d.app_stop("com.whatsapp")
                time.sleep(3)
                self.d.app_start("com.whatsapp", activity="com.whatsapp.HomeActivity")
                time.sleep(10)

            # 定位联系人 并发送消息
            if self.find_contact(receiver):
                self.input_message_click_send(message)
                return True
            else:
                return False

        except Exception as e:
            logger.error("发送消息失败:{}".format(str(e)))
            if 'USB device' in str(e):
                logger.error("设备未连接")
                raise Exception("device_not_found")
            raise Exception("send_message_error")

    # 输入消息并发送
    def input_message_click_send(self, message):
        """
        """
        # 输入消息
        # self.d.send_keys(message)
        self.d(focused=True).set_text(message)
        # 点击发送
        time.sleep(3)
        self.d(resourceId="com.whatsapp:id/conversation_entry_action_button").click()
        time.sleep(2)
        self.d(resourceId="com.whatsapp:id/whatsapp_toolbar_home").click()

    # 定位联系人 并进入聊天界面
    def find_contact(self, receiver):
        """
        找到联系人返回True，否则返回False，异常返回False
        """
        try:
            # 点击搜索框
            self.d(resourceId="com.whatsapp:id/menuitem_search").click()
            time.sleep(2)
            # 输入联系人
            self.d.send_keys(receiver)
            time.sleep(2)
            # 点击联系人
            element = self.d(resourceId="com.whatsapp:id/conversations_row_contact_name", text=receiver)
            if not element.exists:
                self.d.xpath('//android.widget.ImageButton').click()
                time.sleep(2)
                return False
            element.click()
        except Exception as e:
            return False
        return True

    # 重启WhatsApp
    def restart_whatsapp(self):
        self.d.app_stop("com.whatsapp")
        time.sleep(3)
        self.d.app_start("com.whatsapp", activity="com.whatsapp.HomeActivity")
        time.sleep(5)
    #
    def add_contract(self, country_code, contract, message):
        """
        找到联系人返回True，否则返回False，异常返回False
        """
        try:

            time.sleep(2)
            # 退出聊天对话框
            # self.d(resourceId="com.whatsapp:id/whatsapp_toolbar_home").click()
            # time.sleep(2)
            # self.d(resourceId="com.whatsapp:id/transition_start").click()



            # self.d(resourceId="com.whatsapp:id/tab", text="对话").click()
            # self.d(description="新对话").click()
            # 点击新建聊天窗口
            self.d(resourceId="com.whatsapp:id/fab").click()
            time.sleep(2)

            self.d(resourceId="com.whatsapp:id/contactpicker_row_name", text="添加联系人").click()
            time.sleep(2)
            # 选择国家代码
            self.d(resourceId="com.whatsapp:id/country_code_field").click()
            time.sleep(2)
            self.d(resourceId="com.whatsapp:id/country_code", text=country_code).click()
            time.sleep(2)
            self.d(resourceId="com.whatsapp:id/phone_field").set_text(contract)
            time.sleep(2)
            if self.d(resourceId="com.whatsapp:id/number_on_whatsapp_message", text="此人已注册 WhatsApp。").exists:
                self.d(resourceId="com.whatsapp:id/keyboard_aware_save_button").click()
                time.sleep(2)
                self.d(resourceId="com.whatsapp:id/contactpicker_row_name",
                       text="Contact " + country_code + contract).click()
                time.sleep(2)
                self.input_message_click_send(message)
                return True
            else:
                self.d(description="转到上一层级").click()
                time.sleep(1)
                self.d(resourceId="android:id/button2").click()
                time.sleep(1)
                self.d(description="转到上一层级").click()
                return False
        except Exception as e:
            return False
