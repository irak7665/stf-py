# -*- coding: utf-8 -*-
import threading

import redis
from cryptography.fernet import Fernet
import logging
from tools import get_cpu_id, get_mac_address, generate_license_key
from redbapi import Dbapi
dbapi_instance = Dbapi()

# 创建一个logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)  # 设置最低的日志级别

# 创建一个handler，用于写入日志文件
fh = logging.FileHandler('log.log')
fh.setLevel(logging.DEBUG)  # 设置最低的日志级别

# 创建一个handler，用于将日志输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)  # 设置控制台输出的最低日志级别

# 定义handler的输出格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# 给logger添加handler
logger.addHandler(fh)
logger.addHandler(ch)


class redisCloudController:
    def __init__(self):
        self.r = redis.StrictRedis(host='127.0.0.1', port=6379, db=1, decode_responses=True)
        self.key = "PRiO3PpG6f-FMhwap_j8TMnFStYgf5ch-fAz5eNj5nA=".encode('utf-8')
        mac_address = get_mac_address()
        code = generate_license_key(mac_address)
        self.cpuid = code
        try:

            self.cipher = Fernet(self.key)
        except Exception as e:
            print("error:", e)

    # 加密函数
    def encrypt_data(self, data):
        # encrypted_data = self.cipher.encrypt(data)
        encrypted_data = data
        return encrypted_data

    # 解密函数
    def decrypt_data(self, encrypted_data):
        # decrypted_data = self.cipher.decrypt(encrypted_data)
        decrypted_data = encrypted_data
        return decrypted_data

    def get(self, key):
        return self.decrypt_data(self.r.get(self.cpuid + "-" + key))

    def nget(self, key):
        return self.decrypt_data(self.r.get(key))

    def set(self, key, value):
        return self.r.set(self.cpuid + "-" + key, self.encrypt_data(str(value)))

    def hset(self, name, key, value):
        # print("Hset:",self.cpuid+"-"+name, key, value)
        return self.r.hset(self.cpuid + "-" + name, key, self.encrypt_data(str(value)))

    def hget(self, name, key):
        return self.decrypt_data(self.r.hget(self.cpuid + "-" + name, key))

    def hgetall(self, name):
        data = self.r.hgetall(self.cpuid + "-" + name)
        for key in data:
            data[key] = self.decrypt_data(data[key])
        return data

    def hdel(self, name, key):
        return self.r.hdel(self.cpuid + "-" + name, key)

    def hlen(self, name):
        return self.r.hlen(self.cpuid + "-" + name)

    def hkeys(self, name):
        return self.r.hkeys(self.cpuid + "-" + name)

    def hexists(self, name, key):
        return self.r.hexists(self.cpuid + "-" + name, key)


r = redisCloudController()
