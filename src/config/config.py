"""
    Created by howie.hu at 2021/4/7.
    Description：配置文件
        - 命令：PIPENV_DOTENV_LOCATION=./pro.env pipenv run python src/config/config.py
    Changelog: all notable changes to this file will be documented
"""

import os

from src.utils.tools import read_file


class Config:
    """
    配置类
    """

    # 基础配置
    PROJECT_NAME = "LiuLi"
    TIMEZONE = "Asia/Shanghai"
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    # 项目根目录
    PROJECT_DIR = os.path.dirname(BASE_DIR)
    # 版本设置
    VERSION = read_file(os.path.join(PROJECT_DIR, "VERSION"))[0]
    # 模型相关路径
    MODEL_DIR = os.path.join(os.path.join(BASE_DIR, "classifier"), "model_data")
    LL_CONFIG_DIR = os.path.join(PROJECT_DIR, "liuli_config")
    FILE_DIR = os.path.join(PROJECT_DIR, ".files")
    CACHE_DIR = os.path.join(PROJECT_DIR, ".liuli_cache")
    DS_DIR = os.path.join(FILE_DIR, "datasets")
    # API 相关路径
    API_DIR = os.path.join(BASE_DIR, "api")
    API_TEM_DIR = os.path.join(API_DIR, "templates")
    API_TEM_RSS_DIR = os.path.join(API_TEM_DIR, "rss")
    API_TEM_ARTICLE_DIR = os.path.join(API_TEM_DIR, "article")
    API_ACTION_DIR = os.path.join(API_DIR, "views/api")
    # 处理器相关路径
    PROC_DIR = os.path.join(BASE_DIR, "processor")
    PROC_HTML_DIR = os.path.join(PROC_DIR, "html_render")
    PROC_HTML_TMPL_DIR = os.path.join(PROC_HTML_DIR, "tmpl")

    # Flask API配置
    # 固定配置
    LL_HTTP_DEBUG = bool(os.getenv("LL_HTTP_DEBUG", "1") == "1")
    LL_HTTP_HOST = os.getenv("LL_HTTP_HOST", "127.0.0.1")
    LL_HTTP_WORKERS = int(os.getenv("LL_HTTP_WORKERS", "1"))
    LL_HTTP_PORT = 8765

    # 可变配置
    LL_X_TOKEN = os.getenv("LL_X_TOKEN", "hello liuli")
    LL_JWT_SECRET_KEY = os.getenv("LL_JWT_SECRET_KEY", "")
    LL_DOMAIN = os.getenv("LL_DOMAIN", "")

    # 数据库配置
    LL_MONGODB_CONFIG = {
        # "mongodb://0.0.0.0:27027"
        "username": os.getenv("LL_M_USER", ""),
        "password": os.getenv("LL_M_PASS", ""),
        "host": os.getenv("LL_M_HOST", "0.0.0.0"),
        "port": int(os.getenv("LL_M_PORT") or 27027),
        "db": os.getenv("LL_M_DB", "liuli"),
        # 不设置就默认等于 LL_M_DB，针对设置了默认db是admin情况下，想再单独设置操作DB
        "op_db": os.getenv("LL_M_OP_DB", os.getenv("LL_M_DB", "liuli")),
    }

    # 采集器配置
    LL_SPIDER_PROXY = os.getenv("LL_SPIDER_PROXY", "")
    LL_SPIDER_PHANTOMJS_KEY = os.getenv("LL_SPIDER_PHANTOMJS_KEY", "")
    LL_SPIDER_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"

    # 处理器配置
    # 分类器余弦相似度阈值
    LL_COS_VALUE = float(os.getenv("LL_COS_VALUE") or 0.60)

    # 分发器配置
    # 目标支持：ding[钉钉]、wecom[企业微信]、tg[Telegram]
    # 钉钉分发器参数配置，如果 SENDER_LIST 包含 ding ，LL_DD_TOKEN 配置就必须填写
    # 申请钉钉TOKEN时候，关键字必须带有 [liuli]
    LL_DD_TOKEN = os.getenv("LL_DD_TOKEN", "")
    # 企业微信配置
    LL_WECOM_ID = os.getenv("LL_WECOM_ID", "")
    LL_WECOM_AGENT_ID = int(os.getenv("LL_WECOM_AGENT_ID") or 0)
    LL_WECOM_SECRET = os.getenv("LL_WECOM_SECRET", "")
    # 企业微信分发部门，多个部门用;分割
    LL_WECOM_PARTY = os.getenv("LL_WECOM_PARTY", "").split(";")
    # 企业微信分发用户，多个用户用;分割
    LL_WECOM_TO_USER = os.getenv("LL_WECOM_TO_USER", "").replace(";", "|")
    # TG分发器参数配置
    LL_TG_CHAT_ID = os.getenv("LL_TG_CHAT_ID", "")
    LL_TG_TOKEN = os.getenv("LL_TG_TOKEN", "")
    LL_TG_BASE_URL = os.getenv("LL_TG_BASE_URL", "https://api.telegram.org").rstrip("/")
    # Bark 分发器参数配置
    LL_BARK_URL = os.getenv("LL_BARK_URL", "")

    # 备份器配置
    LL_GITHUB_TOKEN = os.getenv("LL_GITHUB_TOKEN", "")
    LL_GITHUB_REPO = os.getenv("LL_GITHUB_REPO", "")
    LL_GITHUB_DOMAIN = os.getenv("LL_GITHUB_DOMAIN", "").rstrip("/")
    LL_GITHUB_BASE_URL = os.getenv("LL_GITHUB_BASE_URL", "https://api.github.com").rstrip("/")
    LL_GITHUB_BACKUP_PATH_IN_REPO = os.getenv("LL_GITHUB_BACKUP_PATH_IN_REPO",
                                              "{doc_source}/{doc_source_name}/{doc_name}.html").lstrip("/")

    @staticmethod
    def set_config(config_data: dict):
        """
        将传入的字典作为配置
        Args:
            config_data (_type_): 配置字典

        Returns:
            _type_: _description_
        """
        for key, value in config_data.items():
            key = str(key).lower()
            if key.startswith("ll_"):
                setattr(Config, key.upper(), value)

    @staticmethod
    def get_config():
        """
        获取 LL 配置
        """
        attributes = {}
        for attr in dir(Config):
            if attr.startswith("LL"):
                attributes[attr] = getattr(Config, attr)
        return attributes


if __name__ == "__main__":
    print(Config.PROJECT_NAME)
    Config.set_config({"LL_PROJECT_NAME": "liuli.io"})
    print(Config.PROJECT_NAME)
    print(Config.LL_MONGODB_CONFIG)
