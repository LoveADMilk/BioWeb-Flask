import os
from PSSMConvert import PSSM

from flask import Flask
import time

app = Flask(__name__)

import json

#!/usr/bin/python
# -*- coding:utf-8 -*-
import pika
import redis


@app.route('/uploadFile/<keyFileName>/')
def index(keyFileName):
    print("接受到的参数为： ", keyFileName)
    # 遍历Redis-key中的列表，放入RabbitMQ
    myRedis = redis.Redis(host='127.0.0.1', port='6379')
    # print(myRedis.exists(keyFileName))
    # print(myRedis.llen(keyFileName))


    # print("输出对应的队列集合" + myRedis.lrange(keyFileName, 0, 2))

    username = 'guest'  # 指定远程rabbitMQ的用户名密码
    pwd = 'guest'
    # 消息队列服务的连接和队列的创建
    credentials = pika.PlainCredentials(username, pwd)
    connection = pika.BlockingConnection(pika.ConnectionParameters('127.0.0.1', 5672, '/', credentials))
    channel = connection.channel()
    # testqueue
    channel.queue_declare(queue='testqueue')

    # 输入的msg
    for i in range(0, myRedis.llen(keyFileName)):
        msg = "已经找到了呢，开始编译第" + str(i) + "文件" + "文件名为： "
        # print(myRedis.lindex(keyFileName, i))
        #生成PSSM文件
        filepath = myRedis.lindex(keyFileName, i)
        filepath = filepath.decode("utf-8")
        print(filepath)
        fromName = filepath
        toName = os.path.splitext(filepath)[0]+'.pssm'
        test = PSSM(fromName, toName)
        test.start()
        # 使用的是默认的交换机，只设置了路径routing_key，这样Java的监听口只许要监听这个队列就行
        channel.basic_publish(exchange='',
                              routing_key='testqueue',
                              body=msg)

    connection.close()

    res = "调用成功呢！"
    return res

@app.route('/collectPapers')
def collectPapers():
    print("访问了这里哦")
    return "OK"

#   返回预测的状态信息
@app.route('/getPredictStatus/<userId>/')
def test(userId):
    print("访问了这里哦 是异步调用")
    username = 'guest'  # 指定远程rabbitMQ的用户名密码
    pwd = 'guest'
    # 消息队列服务的连接和队列的创建
    credentials = pika.PlainCredentials(username, pwd)
    connection = pika.BlockingConnection(pika.ConnectionParameters('127.0.0.1', 5672, '/', credentials))
    channel = connection.channel()
    # testqueue
    channel.queue_declare(queue='testqueue2')
    # JSON 方式传递信息，首先对象无法传递，其次JSON格式统一
    # 由于使用的是异步调用，这里第一个消息是无法在前端显示的，可以做一个sleep
    time.sleep(20)
    data = {
        'userId': userId,
        'status': '这是来自Flask的消息: 状态信息（****1）',
    }
    # 延时后发送，防止消息传递比 建立webSocket早，也为了方便测试
    # time.sleep(20)
    data = json.dumps(data, ensure_ascii=False)
    channel.basic_publish(exchange='',
                          routing_key='testqueue2',
                          body=data)
    time.sleep(20)
    data = {
        'userId': userId,
        'status': '这是来自Flask的消息: 状态信息（****2）',
    }
    # 延时后发送，防止消息传递比 建立webSocket早，也为了方便测试
    # time.sleep(20)
    data = json.dumps(data, ensure_ascii=False)
    channel.basic_publish(exchange='',
                          routing_key='testqueue2',
                          body=data)

    return "OK"

if __name__ == '__main__':
    app.run()
