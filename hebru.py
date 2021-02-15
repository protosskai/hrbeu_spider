import requests
from lxml import etree
import json
from urllib import parse


# GET https://cas-443.wvpn.hrbeu.edu.cn/cas/login?service=https://wvpn.hrbeu.edu.cn/users/auth/cas/callback?url
# //*[@id="fm1"]/li[4]/input[1]
def get_lt(html):
    selector = etree.HTML(html)
    res = selector.xpath("/html/body/div[2]/div[1]/div[2]/div/form/li[4]/input[1]")
    return res[0].get("value")


def get_execution(html):
    selector = etree.HTML(html)
    res = selector.xpath("/html/body/div[2]/div[1]/div[2]/div/form/li[4]/input[2]")
    return res[0].get("value")


def get_JSESSIONID():
    url = "https://cas-443.wvpn.hrbeu.edu.cn/cas/login?service=https://wvpn.hrbeu.edu.cn/users/auth/cas/callback?url"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    r = requests.get(url=url, headers=headers)
    lt = get_lt(r.text)
    execution = get_execution(r.text)
    cookies = r.cookies
    return cookies["JSESSIONID"], lt, execution


# GET https://ehome.wvpn.hrbeu.edu.cn/ HTTP/1.1
# GET https://wvpn.hrbeu.edu.cn/vpn_key/update?origin=https%3A%2F%2Fehome.wvpn.hrbeu.edu.cn%2F&reason=site+ehome.wvpn.hrbeu.edu.cn+not+found
# GET https://wvpn.hrbeu.edu.cn/users/sign_in HTTP/1.1
# GET https://wvpn.hrbeu.edu.cn/users/auth/cas HTTP/1.1

def get_astraeus_session():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    url1 = "https://wvpn.hrbeu.edu.cn/vpn_key/update?origin=https://ehome.wvpn.hrbeu.edu.cn/&reason=site ehome.wvpn.hrbeu.edu.cn not found"
    r = requests.get(url=url1, headers=headers, allow_redirects=False)
    cookies = r.cookies
    url2 = "https://wvpn.hrbeu.edu.cn/users/sign_in"
    r = requests.get(url=url2, headers=headers, cookies=cookies, allow_redirects=False)
    cookies = r.cookies
    url3 = "https://wvpn.hrbeu.edu.cn/users/auth/cas"
    r = requests.get(url=url3, headers=headers, cookies=cookies, allow_redirects=False)
    return r.cookies["_astraeus_session"]


# POST https://cas-443.wvpn.hrbeu.edu.cn/cas/login;jsessionid=60D48E04F3E5CDB4DDCCE6FE2D0D6E77?service=https%3A%2F%2Fwvpn.hrbeu.edu.cn%2Fusers%2Fauth%2Fcas%2Fcallback%3Furl


def get_web_vpn(username, password, JSESSIONID, astraeus_session, lt, execution):
    url = "https://cas-443.wvpn.hrbeu.edu.cn/cas/login;jsessionid={}?service=https://wvpn.hrbeu.edu.cn/users/auth/cas/callback?url"
    url = url.format(JSESSIONID)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://cas-443.wvpn.hrbeu.edu.cn",
        "HOST": "cas-443.wvpn.hrbeu.edu.cn",
        "Referer": "https://cas-443.wvpn.hrbeu.edu.cn/cas/login?service=https://wvpn.hrbeu.edu.cn/users/auth/cas/callback?url"
    }
    data = {
        "username": username,
        "password": password,
        "captcha": "",
        "lt": lt,
        "execution": execution,
        "_eventId": "submit",
        "submit": "登 录"
    }
    jar = requests.cookies.RequestsCookieJar()
    jar.set('MESSAGE_TICKET', '%7B%22times%22%3A0%7D')
    jar.set('JSESSIONID', JSESSIONID)
    data = parse.urlencode(data)
    r = requests.post(url=url, headers=headers, data=data, cookies=jar, allow_redirects=False)
    cookies = r.cookies
    CASTGC = cookies.get("CASTGC")
    next_url = r.next.url
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "HOST": "wvpn.hrbeu.edu.cn",
        "Referer": "https://cas-443.wvpn.hrbeu.edu.cn/cas/login?service=https://wvpn.hrbeu.edu.cn/users/auth/cas/callback?url"
    }
    jar = requests.cookies.RequestsCookieJar()
    jar.set('_astraeus_session', astraeus_session)
    jar.set('SERVERID', "Server1")
    r = requests.get(url=next_url, headers=headers, cookies=jar, allow_redirects=False)
    cookies = r.cookies
    _astraeus_session = cookies.get("_astraeus_session")
    url = "https://wvpn.hrbeu.edu.cn/vpn_key/update"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "https://cas-443.wvpn.hrbeu.edu.cn/cas/login?service=https://wvpn.hrbeu.edu.cn/users/auth/cas/callback?url"
    }
    jar = requests.cookies.RequestsCookieJar()
    jar.set('_astraeus_session', _astraeus_session)
    r = requests.get(url, headers=headers, cookies=jar, allow_redirects=False)
    cookies = r.cookies
    _webvpn_key = cookies.get("_webvpn_key")
    webvpn_username = cookies.get("webvpn_username")
    _astraeus_session = cookies.get("_astraeus_session")
    return _webvpn_key, webvpn_username, _astraeus_session, CASTGC


def get_SESS(_webvpn_key, webvpn_username, CASTGC):
    url = "https://ehome.wvpn.hrbeu.edu.cn/cas"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "HOST": "ehome.wvpn.hrbeu.edu.cn",
        "Referer": "https://cas-443.wvpn.hrbeu.edu.cn/cas/login?service=https://wvpn.hrbeu.edu.cn/users/auth/cas/callback?url"
    }
    jar = requests.cookies.RequestsCookieJar()
    jar.set('_webvpn_key', _webvpn_key)
    jar.set('webvpn_username', webvpn_username)
    r = requests.get(url=url, headers=headers, cookies=jar, allow_redirects=False)
    cookies = r.cookies
    SESS = cookies.get("SESS0ff61cb4d0d756921e9a212fbfc27ce5")
    url = "https://cas.wvpn.hrbeu.edu.cn/cas/login?service=https://ehome.wvpn.hrbeu.edu.cn/cas"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "HOST": "cas.wvpn.hrbeu.edu.cn",
        "Referer": "https://cas-443.wvpn.hrbeu.edu.cn/cas/login?service=https://wvpn.hrbeu.edu.cn/users/auth/cas/callback?url"
    }
    jar = requests.cookies.RequestsCookieJar()
    jar.set('_webvpn_key', _webvpn_key)
    jar.set('webvpn_username', webvpn_username)
    jar.set("SESS0ff61cb4d0d756921e9a212fbfc27ce5", SESS)
    r = requests.get(url=url, headers=headers, cookies=jar, allow_redirects=False)
    url = "https://cas-443.wvpn.hrbeu.edu.cn/cas/login?service=https://ehome.wvpn.hrbeu.edu.cn/cas"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "HOST": "cas-443.wvpn.hrbeu.edu.cn",
        "Referer": "https://cas-443.wvpn.hrbeu.edu.cn/cas/login?service=https://wvpn.hrbeu.edu.cn/users/auth/cas/callback?url"
    }
    jar.set("MESSAGE_TICKET", "%7B%22times%22%3A0%7D")
    jar.set("CASTGC", CASTGC)
    r = requests.get(url=url, headers=headers, cookies=jar, allow_redirects=False)
    next_url = r.next.url
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "HOST": "ehome.wvpn.hrbeu.edu.cn",
        "Referer": "https://cas-443.wvpn.hrbeu.edu.cn/cas/login?service=https://wvpn.hrbeu.edu.cn/users/auth/cas/callback?url"
    }
    jar = requests.cookies.RequestsCookieJar()
    jar.set('_webvpn_key', _webvpn_key)
    jar.set('webvpn_username', webvpn_username)
    jar.set("SESS0ff61cb4d0d756921e9a212fbfc27ce5", SESS)
    r = requests.get(url=next_url, headers=headers, cookies=jar, allow_redirects=False)
    url = "https://ehome.wvpn.hrbeu.edu.cn/cas"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "HOST": "ehome.wvpn.hrbeu.edu.cn",
        "Referer": "https://cas-443.wvpn.hrbeu.edu.cn/cas/login?service=https://wvpn.hrbeu.edu.cn/users/auth/cas/callback?url"
    }
    r = requests.get(url=url, headers=headers, cookies=jar, allow_redirects=False)
    cookies = r.cookies
    SESS = cookies.get("SESS0ff61cb4d0d756921e9a212fbfc27ce5")
    return SESS


def get_main_page(_webvpn_key, webvpn_username, SESS):
    url = "https://ehome.wvpn.hrbeu.edu.cn/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "HOST": "ehome.wvpn.hrbeu.edu.cn",
        "Referer": "https://cas-443.wvpn.hrbeu.edu.cn/cas/login?service=https://wvpn.hrbeu.edu.cn/users/auth/cas/callback?url"
    }
    jar = requests.cookies.RequestsCookieJar()
    jar.set('_webvpn_key', _webvpn_key)
    jar.set('webvpn_username', webvpn_username)
    jar.set("SESS0ff61cb4d0d756921e9a212fbfc27ce5", SESS)
    r = requests.get(url=url, headers=headers, cookies=jar)
    print(r.text)


def get_jkgc_JSESSIONID(_webvpn_key, webvpn_username):
    url = "https://cas.hrbeu.edu.cn/cas/login?service=http://jkgc.hrbeu.edu.cn/infoplus/login?retUrl=http://jkgc.hrbeu.edu.cn/infoplus/form/JSXNYQSBtest/start"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "HOST": "cas.hrbeu.edu.cn"
    }
    jar = requests.cookies.RequestsCookieJar()
    jar.set('_webvpn_key', _webvpn_key)
    jar.set('webvpn_username', webvpn_username)
    r = requests.get(url=url, headers=headers, cookies=jar, allow_redirects=False)
    html = r.text
    cookies = r.cookies
    lt = get_lt(html)
    execution = get_execution(html)
    return cookies.get("JSESSIONID"), lt, execution


def jkgc_login(username, password, _webvpn_key, webvpn_username, JSESSIONID, lt, execution):
    url = "https://cas.hrbeu.edu.cn/cas/login;jsessionid={}?service=http://jkgc.hrbeu.edu.cn/infoplus/login?retUrl=http://jkgc.hrbeu.edu.cn/infoplus/form/JSXNYQSBtest/start"
    url = url.format(JSESSIONID)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Content-Type": "application/x-www-form-urlencoded",
        "HOST": "cas.hrbeu.edu.cn",
        "Origin": "https://cas.hrbeu.edu.cn",
        "Referer": "https://cas.hrbeu.edu.cn/cas/login?service=http://jkgc.hrbeu.edu.cn/infoplus/login?retUrl=http://jkgc.hrbeu.edu.cn/infoplus/form/JSXNYQSBtest/start"
    }
    jar = requests.cookies.RequestsCookieJar()
    jar.set('_webvpn_key', _webvpn_key)
    jar.set('webvpn_username', webvpn_username)
    jar.set('JSESSIONID', JSESSIONID)
    jar.set('MESSAGE_TICKET', "%7B%22times%22%3A0%7D")

    data = {
        "username": username,
        "password": password,
        "captcha": "",
        "lt": lt,
        "execution": execution,
        "_eventId": "submit",
        "submit": "登 录"
    }
    data = parse.urlencode(data)
    r = requests.post(url=url, headers=headers, data=data, cookies=jar, allow_redirects=False)
    cookies = r.cookies
    print(cookies.get("CASTGC"))


username = input("输入你的学号：")
password = input("输入你的密码：")
JSESSIONID, lt, execution = get_JSESSIONID()
astraeus_session = get_astraeus_session()
_webvpn_key, webvpn_username, _astraeus_session, CASTGC = get_web_vpn(username, password, JSESSIONID, astraeus_session,
                                                                      lt, execution)
JSESSIONID, lt, execution = get_jkgc_JSESSIONID(_webvpn_key, webvpn_username)
jkgc_login(username, password, _webvpn_key, webvpn_username, JSESSIONID, lt, execution)
