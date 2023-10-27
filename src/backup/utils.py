"""
    Created by howie.hu at 2022-01-25.
    Description: 存储器通用函数
    Changelog: all notable changes to this file will be documented
"""

from src.common.remote import get_html_by_requests, get_wechat_html_by_requests
from src.config import Config
from src.processor.html_render import render_book_html
from src.utils.tools import text_decompress
import requests
import json
import base64


def retry_func(func, url, max_retries=3):
    for i in range(max_retries):
        try:
            result = func(url)
        except Exception as e:
            print(f"Retry {i + 1} failed, retrying...")
            continue
        if result is not None:
            return result
        print(f"Retry {i + 1} failed, retrying...")
    return None


def get_bak_doc_html(doc_data: dict, doc_html_type: str = "default") -> str:
    """返回不同doc_html类型下的最终html

    Args:
        doc_html_type (str): 各种获取doc_html的方式
            - default: 默认，获取doc_data里面的doc_html数据，不存在就使用online
            - online: 进行网络获取
            - book: 进行二次渲染，这里是渲染成书籍阅读主题
            - wechat: 使用 selenium 进行抓取，并进行修改，以便保留样式
        doc_data (dict): 文章数据

    Returns:
        str: 处理后的 doc_html
    """
    # 获取原始文本内容
    doc_link = doc_data["doc_link"]
    online_func = lambda url: get_html_by_requests(
        url=url, headers={"User-Agent": Config.LL_SPIDER_UA}
    )
    wechat_func = lambda url: retry_func(get_wechat_html_by_requests, url)
    if doc_html_type == "online":
        doc_html = online_func(doc_link)
    elif doc_html_type == "book":
        doc_source_name = doc_data.get("doc_source_name", "")
        doc_name = doc_data.get("doc_name", "")
        doc_core_html = text_decompress(doc_data.get("doc_core_html", ""))
        doc_html = render_book_html(doc_source_name, doc_name, doc_core_html)
    elif doc_html_type == "wechat":
        doc_html = wechat_func(doc_link)
    else:
        # 本地模式
        doc_html = text_decompress(doc_data.get("doc_html")) or online_func(doc_link)

    return doc_html


class GitHubRepo:
    BASE_URL = "{base_url}/repos/{repo}/contents/"

    def __init__(self, token, repo, base_url="https://api.github.com"):
        self.token = token
        self.repo = repo
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.base_url = base_url

    def get_contents(self, path):
        response = requests.get(self.BASE_URL.format(base_url=self.base_url, repo=self.repo) + path,
                                headers=self.headers)
        if response.status_code == 200:
            file_info = response.json()
            content = base64.b64decode(file_info["content"]).decode("utf-8")
            return content
        else:
            return None

    def update_file(self, path, content, message):
        file_info = requests.get(self.BASE_URL.format(base_url=self.base_url, repo=self.repo) + path,
                                 headers=self.headers).json()
        sha = file_info["sha"]

        data = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
            "sha": sha
        }
        response = requests.put(self.BASE_URL.format(base_url=self.base_url, repo=self.repo) + path,
                                headers=self.headers,
                                data=json.dumps(data))
        return response.status_code == 200

    def create_file(self, path, content, message):
        data = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("utf-8")
        }
        response = requests.put(self.BASE_URL.format(base_url=self.base_url, repo=self.repo) + path,
                                headers=self.headers,
                                data=json.dumps(data))
        return response.status_code == 201

    def delete_file(self, path, message):
        file_info = requests.get(self.BASE_URL.format(base_url=self.base_url, repo=self.repo) + path,
                                 headers=self.headers).json()
        sha = file_info["sha"]

        data = {
            "message": message,
            "sha": sha
        }
        response = requests.delete(self.BASE_URL.format(base_url=self.base_url, repo=self.repo) + path,
                                   headers=self.headers,
                                   data=json.dumps(data))
        return response.status_code == 200


