import selenium
import urllib3
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys  # 引入键盘指令包
from selenium.webdriver.support.select import Select  # 下拉标签
from selenium.webdriver.chrome.options import Options  # 浏览器设置
import re
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def main(url, title):
    url = 'https://www.manga2022.com/warningConfirm?redirect=' + url
    web = Chrome(options=opt)
    # web.set_window_size(200,400)
    web.get(url)
    time.sleep(12)
    for i in range(60):  # 滚动界面，让每个图片加载
        web.execute_script(f'window.scrollBy(0, {100 + 10 * i})')
        time.sleep(0.011)
        web.execute_script(f'window.scrollBy(0, -{100 + 5 * i})')
        # time.sleep(1)
    links = obj_link.finditer(web.page_source)
    title_date = f'{date}/{title}'
    mkdir(date)
    mkdir(title_date)
    name = 1
    with ThreadPoolExecutor(30) as f:
        for link in links:
            link = link.group('link')
            f.submit(download, link, title_date,name)
            name += 1
            # time.sleep(0.05)
    web.close()
    web.quit()


# 创建文件夹
def mkdir(path):
    import os
    path = path.strip()
    path = path.rstrip("\\")
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        print(path + ' 创建成功')
        return True
    else:
        return False


def download(link, date , name):
    if link != 0:
        mkdir(f'{date}')
        # name = obj_name.search(link).group('name')
        date = f'{date}/{name}.png'
        with open(date, 'wb') as f:
            try:
                f.write(requests.get(link, verify=False).content)
                print(f'{date}下载完成')
            except urllib3.exceptions.MaxRetryError or urllib3.exceptions.NewConnectionError:
                pass


def find_ual(url):
    url = 'https://www.manga2022.com/warningConfirm?redirect=' + url
    web = Chrome(options=opt)
    web.get(url)
    time.sleep(1)
    title = []
    pagelink = []
    # print(web.page_source)
    all_page_links = obj_all_pagelink.search(web.page_source).group('allpagelink')  # 三层标签中的所有这个标签
    anime_name = obj_anime_name.search(web.page_source).group('name')
    page_links = obj_pagelink_title.finditer(all_page_links)  # 所有这个标签里的所有链接
    for page_link in page_links:
        title.append(page_link.group('title'))
        pagelink.append(page_link.group('pagelink'))
    return title, pagelink, anime_name


if __name__ == '__main__':
    obj_link = re.compile(r'<li><img data-src="(?P<link>.*?)" src=".*?', re.S)
    # obj_name = re.compile(r'/\d\d\d\d\d\d\d\d\d\d\d\d(?P<name>.*?).jpg.h800x.*?')
    obj_all_pagelink = re.compile(r'<div id="default全部"(?P<allpagelink>.*?)<a href="javascript:;">')
    obj_pagelink_title = re.compile(r'<a href="(?P<pagelink>.*?)" target="_blank" title="(?P<title>.*?)" s')
    obj_anime_name = re.compile(r'<h6 title="(?P<name>.*?)">')
    opt = Options()
    opt.add_argument("--headless")
    opt.add_argument("--disable-gpu")
    start = time.time()
    url = input('url>>>')
    ii = input('从第几话开始>>>')
    if len(ii) == 0:
        ii = 0
    else:
        ii = int(ii) - 1
    iii = ii + 1
    find_uals = find_ual(url)
    titles = find_uals[0]  # 第  话
    urls = find_uals[1]  # 第 话的链接
    anime_name = find_uals[2]
    date = f'D:/桌面/漫画/{anime_name}'
    with ThreadPoolExecutor(20) as f:
        for url in urls[ii:]:
            # f.submit(main, url, titles[iii])  # 文件夹为每一话的官网名字，下完后排列顺序会不对
            f.submit(main, url, f'{iii} + {titles[iii-1]}')  # 文件夹名字为下载次序 + 官网名字
            iii += 1
    finish = time.time()
    print(f'完成所有！一共{iii + 1}话')
    print(f'共耗时{finish-start}')
