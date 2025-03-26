#!/usr/bin/env python

import os
import requests as r
import time
from xml.etree import ElementTree as ET

import logging
logging.basicConfig(format="[%(asctime)s] [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger("get_last_sms")

TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
TG_URL = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
TG_CHAN_ID = os.environ.get("TG_CHAN_ID")

LIST_SMS_URL = "http://192.168.8.1/api/sms/sms-list"
LIST_SMS = """<?xml version "1.0" encoding="UTF-8"?>
    <request>
        <PageIndex>1</PageIndex><ReadCount>1</ReadCount>
        <BoxType>1</BoxType><SortType>0</SortType>
        <Ascending>0</Ascending>
        <UnreadPreferred>0</UnreadPreferred>
    </request>"""
DELETE_SMS_URL = "http://192.168.8.1/api/sms/delete-sms"


class Message:
    def __init__(self, xml_root):
        self.__index = xml_root.find(".//Messages/Message/Index").text
        self.__date = xml_root.find(".//Messages/Message/Date").text
        self.__sender = xml_root.find(".//Messages/Message/Phone").text
        self.__content = xml_root.find(".//Messages/Message/Content").text

    @property
    def index(self):
        return self.__index

    @property
    def date(self):
        return self.__date

    @property
    def sender(self):
        return self.__sender

    @property
    def content(self):
        return self.__content

# NB: Set up a routing in order to access the Internet
def tg_send_sms(text):
    data = dict(chat_id=TG_CHAN_ID, text=text)
    resp = r.post(TG_URL, json=data)

def delete_sms(index):
    delete_sms_req = f'<?xml version="1.0" encoding="UTF-8"?><request><Index>{index}</Index></request>'
    resp = r.post(DELETE_SMS_URL, data=delete_sms_req)

def get_last_msg():
    resp = r.post(LIST_SMS_URL, data=LIST_SMS)
    resp.encoding = "UTF-8"
    xml_data = ET.fromstring(resp.text)
    return xml_data

def receive_sms():
    logger.info(f"Started receiving sms from {LIST_SMS_URL}")
    while True:
        xml_data = get_last_msg()
        sms_count = int(xml_data.find(".//Count").text)

        if sms_count > 0:
            msg = Message(xml_data)
            logger.info(f"Received sms {msg.index} from {msg.sender}")
            tg_send_sms(msg.date + "\n" + msg.sender + "\n" + msg.content)
            logger.info(f"Sent sms {msg.index} to telegram")
            delete_sms(msg.index)
            logger.info(f"Deleted sms {msg.index} from {msg.sender}")

        time.sleep(3)

if __name__ == "__main__":
    receive_sms()
