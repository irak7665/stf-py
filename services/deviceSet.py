import globals_


# 设置设备状态
# 0:运行中 1:已停止 2:暂停 3:停止过程中
def setDeviceStatus(serial, status):
    globals_.r.hset("device_status", serial, status)
