# -*- coding: utf-8 -*-
import hashlib
import json
import os
import platform
import uuid

import pandas as pd
import re


def get_mac_address():
    mac = uuid.getnode()
    mac_address = ':'.join([format((mac >> elements) & 0xff, '02x') for elements in range(2, 10, 2)][::-1])
    return mac_address


def generate_license_key(input_string: str) -> str:
    """Generate a unique license key based on the input string."""
    make_str = input_string + "michael"
    sha256_hash = hashlib.sha256()
    sha256_hash.update(make_str.encode('utf-8'))
    license_key = sha256_hash.hexdigest().upper()

    # Optionally format the key in the typical XXXX-XXXX-XXXX-XXXX format
    license_key = '-'.join([license_key[i:i + 4] for i in range(0, len(license_key), 4)])

    return license_key


def get_cpu_id():
    try:
        if platform.system() == "Windows":
            lines = os.popen("wmic cpu get ProcessorId").read().split("\n")
            for line in lines:
                if "ProcessorId" not in line and line.strip() != "":
                    return line.strip()
        else:
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Path: app\services\tools.py
# 从excel中读取数据
def read_excel_data(filename):
    try:
        df = pd.read_excel(filename, dtype=str)
        result = [{'rec': row['rec']} for _, row in df.iterrows()]
    except Exception as e:
        print(e)
        result = False
    return result


def read_excel_contract(filename):
    try:
        df = pd.read_excel(filename, dtype=str)
        # redis_contract_data = []
        #
        # # 用于验证country_code和contract的正则表达式
        # country_code_pattern = re.compile(r'^\+\d+$')
        # contract_pattern = re.compile(r'^\d+$')
        # # print("country_code_pattern:", country_code_pattern, "contract_pattern:", contract_pattern)
        #
        # # 遍历每一行
        # for index, row in df.iterrows():
        #     country_code = str(row.get("country_code", "")).strip()
        #     contract = str(row.get("contract", "")).strip()
        #
        #     # 检查country_code和contract是否都有数据
        #     if not country_code or not contract:
        #         print("not country_code or not contract:", country_code, contract)
        #         continue
        #
        #     # 检查数据格式
        #     if not country_code_pattern.match(country_code) or not contract_pattern.match(contract):
        #         print("not match:", country_code, contract)
        #         continue
        #
        #     # 保存到redis
        #     redis_contract_data.append({"country_code": country_code, "contract": contract})
        #
        # result = redis_contract_data
        result = [{'country_code': row['country_code'], 'contract': row['contract']} for _, row in df.iterrows()]
        print("read_excel_contract:", result)
    except Exception as e:
        print("read_excel_contract:", e)
        result = False
    return result


def response_json(status='ok', msg='', data='', code=200):
    return {'code': code, 'status': status, 'msg': msg, 'data': data}


# 获取硬盘唯一id

def get_disk_serial():
    cmd = 'vol C:'
    result = os.popen(cmd).read()
    lines = result.split("\n")
    for line in lines:
        if "Volume Serial Number" in line:
            serial_number = line.split(" is ")[1].strip()
            return serial_number
    return None
