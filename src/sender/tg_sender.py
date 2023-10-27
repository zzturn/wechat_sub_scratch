#!/usr/bin/env python
"""
    Created by seven at 2021/12/27.
    Description：分发到Telegram
    Changelog: all notable changes to this file will be documented
"""

import time

from src.common.remote import send_post_request
from src.config import Config
from src.sender.base import SenderBase
from src.utils import LOGGER

TG_BOT_MSG_TEMPLATE = """
<strong>作者: {doc_source_name}</strong>
{doc_cus_des}<a href="{doc_link}"><b>{doc_name}</b></a>

<pre>更新时间: {doc_date}</pre>
"""


class TGSender(SenderBase):
    """
    Telegram分发类
    """

    def __init__(self, init_config: dict):
        """
        初始化相关变量
        :param init_config:
        """
        super().__init__(send_type="tg", init_config=init_config)
        self.chat_id = init_config.get("tg_chat_id", Config.LL_TG_CHAT_ID)
        self.token = init_config.get("tg_token", Config.LL_TG_TOKEN)
        self.url = f"{Config.LL_TG_BASE_URL}/bot{self.token}/sendMessage"

    def send(self, send_data) -> bool:
        """
        下发到Telegram
        :param send_data: 下发内容字典，字段开发者自定义
        :return:
        """
        doc_id = send_data["doc_id"]
        doc_name = send_data["doc_name"]
        doc_link = send_data["doc_link"]
        doc_cus_des = send_data["doc_cus_des"]
        doc_source_name = send_data["doc_source_name"]
        is_send = self.is_send(doc_id=doc_id)

        send_status = True
        if not is_send:
            message = TG_BOT_MSG_TEMPLATE.format_map(send_data)
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": "yes",
            }
            resp_dict = send_post_request(
                url=self.url,
                data=data,
                headers={"Content-Type": "application/json"},
                timeout=5,
            )
            notice_msg = f"{doc_cus_des}👉{doc_source_name}_{doc_name}：{doc_link} 分发到 {self.send_type}"
            if resp_dict:
                if resp_dict.get("ok") is True:
                    # 将状态持久化到数据库
                    self.sl_coll.insert_one(
                        {
                            "send_type": self.send_type,
                            "doc_id": doc_id,
                            "ts": int(time.time()),
                        }
                    )
                    # 下发成功
                    LOGGER.info(f"{notice_msg} 成功！")
                else:
                    LOGGER.error(f"{notice_msg} 失败：{resp_dict.get('errmsg')}")
                    send_status = False
            else:
                LOGGER.error(f"{notice_msg} 失败!")
                send_status = False

        return send_status


def send(init_config: dict, send_data: dict) -> bool:
    """
    下发到Telegram
    :param init_config: 下发终端配置
    :param send_data: 下发内容字典，字段开发者自定义
    :return:
    """
    return TGSender(init_config=init_config).send(send_data)


if __name__ == "__main__":
    send(
        init_config={
            "tg_chat_id": "",
            "tg_token": "",
        },
        send_data={
            "doc_id": "f42460107f69c9e929f8d591243efeb2",
            "doc_date": "2021-04-11",
            "doc_des": "",
            "doc_ext": {},
            "doc_link": "https://mp.weixin.qq.com/s/J9Ejaw9x9fXDZ4-hsrhhtw",
            "doc_name": "普通人搞一百万有多难？",
            "doc_source": "wechat",
            "doc_source_des": "前码农&产品人，现自由职业者，创业者。",
            "doc_source_name": "stormzhang",
            "doc_cus_des": "广告",
            "doc_keywords": ["一百万"],
            "doc_ts": 1618136819.0,
            "cos_model": {
                "model_name": "cos",
                "result": 0,
                "probability": 0.0,
                "feature_dict": {
                    "is_black": False,
                    "is_white": False,
                    "text": "普通人搞一百万有多难？",
                },
            },
        },
    )
