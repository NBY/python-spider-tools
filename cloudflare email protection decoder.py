"""
用于绕过cloudflare验证
将加密后的电子邮件内容还原为原始邮件地址

20211006
Alexander Nie
"""

import cloudscraper
from cloudscraper import HTTPAdapter
from lxml import html
import re


COOKIES = {}

HEADERS = {}


def get(url):
    """
    使用cloudscraper绕过cloudflare的防护
    """
    scraper = cloudscraper.create_scraper( )
    scraper.mount('http://', HTTPAdapter(max_retries=3))
    scraper.mount('https://', HTTPAdapter(max_retries=3))
    try:
        response = scraper.get(url, cookies=COOKIES, headers=HEADERS, timeout=10)
        while response.status_code != 200:
            response = scraper.get(url, cookies=COOKIES, headers=HEADERS, timeout=10)
            return response
        return response
    except Exception as e:
        print(e)


def cfDecodeEmail(encodedString):
    """
    解码邮件地址
    """
    r = int(encodedString[:2], 16)
    email = ''.join([chr(int(encodedString[i:i + 2], 16) ^ r) for i in range(2, len(encodedString), 2)])
    return email


def cf_mail_decoder(url):
    """
    主要功能
    将cloudflare加密后的电子邮件地址还原
    返回response
    """
    response = get(url)
    response_text = response.text
    tree = html.fromstring(response.text)
    cf_mail = tree.xpath("//a[@class='__cf_email__']")
    if cf_mail:
        for i in cf_mail:
            code = i.get("data-cfemail")
            decode = cfDecodeEmail(code)
            tagregex = r'<a href="\/cdn-cgi\/l\/email-protection"[^>]*>([^<]+)<\/a>'
            res = re.search(tagregex, response_text)
            response_text = response_text.replace(res.group( ), decode)
        return response_text
    return response_text

#print(cf_mail_decoder("https://example.com/"))
