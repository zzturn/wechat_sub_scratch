"""
    Created by howie.hu at 2021-12-30.
    Description: 外部调用相关请求
    Changelog: all notable changes to this file will be documented
"""
import json

import cchardet
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from src.utils import LOGGER


def get_html_by_phantomjs(url: str, sk_key: str):
    """
    基于 phantomjs 获取html
    """
    data = {
        "url": url,
        "renderType": "html",
        # "waitForSelector": "",
    }
    url = f"http://PhantomJScloud.com/api/browser/v2/{sk_key}/"
    html = ""
    try:
        req = requests.post(url, data=json.dumps(data), timeout=60)
        html = req.text
    except Exception as e:
        LOGGER.error(f"通过 Phantomjs 请求 {url} 失败! {e}")
    return html


def get_html_by_requests(url: str, params: dict = None, timeout: int = 3, **kwargs):
    """发起GET请求，获取文本

    Args:
        url (str): 目标网页
        params (dict, optional): 请求参数. Defaults to None.
        timeout (int, optional): 超时时间. Defaults to 3.
    """
    resp = send_get_request(url=url, params=params, timeout=timeout, **kwargs)
    text = None
    try:
        content = resp.content
        charset = cchardet.detect(content)
        text = content.decode(charset["encoding"])
    except Exception as e:
        LOGGER.exception(f"请求内容提取出错 - {url} - {str(e)}")
    return text


options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Remote(
    command_executor='http://selenium_chrome:4444/wd/hub',
    options=options)

def get_wechat_html_by_requests(url: str):
    """发起GET请求，获取文本

    Args:
        url (str): 目标网页
    """
    # resp = send_get_request(url=url, params=params, timeout=timeout, **kwargs)
    text = None
    try:


        driver.get(url)

        # 等待JavaScript执行完毕
        driver.implicitly_wait(5)  # 等待5秒，你可以根据实际情况调整这个时间

        # 获取网页源代码
        source = driver.page_source
        new_soup = BeautifulSoup(source, 'html.parser')

        # 找到所有的<img>标签，将图片的src属性设置为data-src属性的值，并生成外链
        img_tags = new_soup.find_all('img')
        for img in img_tags:
            # 如果<img>标签有data-src属性
            if img.has_attr('data-src'):
                # 将src属性设置为data-src属性的值
                img['src'] = 'https://images.weserv.nl/?url=' + img['data-src']

        # 找到所有的<link>标签，如果href属性的值不是以https:开头，则添加https:前缀
        link_tags = new_soup.find_all('link')
        for link in link_tags:
            # 如果<link>标签有href属性
            if link.has_attr('href'):
                # 如果href属性的值不以https:开头
                if not link['href'].startswith('https:') and not link['href'].startswith('http:'):
                    # 在href属性的值前面添加https:
                    link['href'] = 'https:' + link['href']

        # 找到所有的<script>标签，删除这些标签
        script_tags = new_soup.find_all('script')
        for script in script_tags:
            # 删除<script>标签
            script.decompose()

        text = new_soup.prettify()
    except Exception as e:
        LOGGER.exception(f"请求内容提取出错 - {url} - {str(e)}")
    return text


def send_get_request(url: str, params: dict = None, timeout: int = 3, **kwargs):
    """发起GET请求

    Args:
        url (str): 目标地址
        params (dict, optional): 请求参数. Defaults to None.
        timeout (int, optional): 超时时间. Defaults to 3.

    Returns:
        [type]: [description]
    """
    try:
        resp = requests.get(url, params, timeout=timeout, **kwargs)
    except Exception as e:
        resp = None
        LOGGER.exception(f"请求出错 - {url} - {str(e)}")
    return resp


def send_post_request(url: str, data: dict = None, timeout: int = 5, **kwargs) -> dict:
    """发起post请求

    Args:
        url (str): 目标地址
        data (dict, optional): 请求参数. Defaults to None.
        timeout (int, optional): 超时时间. Defaults to 5.

    Returns:
        dict: [description]
    """
    try:
        resp_dict = requests.post(
            url, data=json.dumps(data), timeout=timeout, **kwargs
        ).json()
    except Exception as e:
        resp_dict = {}
        LOGGER.error(f"请求出错：{e}")
    return resp_dict
