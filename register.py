import time

import netifaces
import redis


def get_mac_addresses():
    mac_addresses = {}
    for interface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(interface)
        try:
            mac_addresses[interface] = addrs[netifaces.AF_LINK][0]['addr']
        except KeyError:
            # 该接口可能没有 MAC 地址
            print("Error...,can't find the params, please contact the manager")
    return mac_addresses

macs = get_mac_addresses()
while True:
    try:
        r = redis.StrictRedis(host='127.0.0.1', port=6379, db=1, decode_responses=True)

        for interface, mac in macs.items():
            if mac != '00:00:00:00:00:00' and 'docker' not in interface:
                print(f"Interface: {interface}, MAC Address: {mac}")
                r.set('macaddress', mac,ex=601)
                redis_mac = r.get('macaddress')
                print('redis mac:',redis_mac)
                break
    except:
        print("Register run error...please contact the manager")
    time.sleep(600)
