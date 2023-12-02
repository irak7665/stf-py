import redis
import time

client = redis.StrictRedis(host='localhost', port=6379, db=1)

while True:
    message = "12"
    client.publish('my-channel', message)
    print(f'Sent message: {message}')
    time.sleep(1)  # 每秒发送一条消息
