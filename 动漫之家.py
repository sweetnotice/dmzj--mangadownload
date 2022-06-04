import re
import requests
from concurrent.futures import ThreadPoolExecutor
import time
import selenium
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys  # 引入键盘指令包
from selenium.webdriver.support.select import Select  # 下拉标签
from selenium.webdriver.chrome.options import Options  # 浏览器设置


def mkdir(path):
    import os
    path = path.strip()
    path = path.rstrip("\\")
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        # print(path + ' 创建成功\n', end='')
        return True
    else:
        # print(' 创建过了')
        return False


def get_all_urls(url):  # 获取每一章的链接
    driver = Chrome(options=option)
    driver.get(url)
    try:
        driver.find_element(By.XPATH, value='//*[@id="list"]/ul[1]/li[12]').click()
    except selenium.common.exceptions.NoSuchElementException:
        pass
    url_lists = []
    links = obj_get_all_urls.finditer(driver.page_source)
    for link in links:
        link = 'https://m.dmzj.com/' + link.group('link')
        # print(link)
        url_lists.append(link)
    driver.close()
    driver.quit()
    return url_lists


def download(url, name, data):
    resp = requests.get(url, headers=headers).content
    third_data = data + f'/{name}'
    with open(f'{third_data}.jpg', 'wb') as f:
        f.write(resp)
        # print(f'{third_data}.jpg下载完成\n', end='')


def main(url):
    driver = Chrome(options=option)
    driver.get(url)
    picture_links = obj_get_all_picture_urls.finditer(driver.page_source)
    title = driver.title.replace('_', '/').replace('漫画-动漫之家手机漫画', '')  # xxxxx_第x话 -->/xxxxx/第x话
    show_title = title.split('/')[1]
    second_data = first_data + f'/{title}'
    mkdir(second_data)
    ii = 1
    # print(driver.page_source)
    with ThreadPoolExecutor(10) as f:  # 下载
        for picture_link in picture_links:
            picture_link = 'https://images.dmzj.com/' + picture_link.group('link')
            # print(picture_link)
            f.submit(download, picture_link, ii, second_data)
            ii += 1
    print(f'{show_title}  下载完毕\n', end='')


if __name__ == '__main__':
    obj_get_all_picture_urls = re.compile(r'data-original="https://images.dmzj.com/(?P<link>.*?)" class="comic_img"',
                                          re.S)
    obj_get_all_urls = re.compile(r'<a href="(?P<link>.*?)".onclick="chapterCookie')
    option = Options()
    option.add_argument(
        'user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"')

    # 下面两行是无头浏览器的，如果想看到浏览器的话就把它俩删了
    option.add_argument("--headless")
    option.add_argument("--disable-gpu")

    headers = {
        'Referer': 'https://m.dmzj.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
    }
    first_data = 'D:/漫画'  # 可以自行更改存放路径
    mkdir(first_data)
    # url = 'https://m.dmzj.com/view/19081/131014.html'
    # url = 'https://manhua.dmzj.com/fwlbsrstgjljcswszj'  # 电脑的
    # url = 'https://m.dmzj.com/info/fwlbsrstgjljcswszj.html' # 手机的
    # url = input('输入链接(必须为手机版的地址)>>>')  # 书架地址为 https://m.dmzj.com/subscribe.html
    url = input('请输入地址>>>').replace('manhua.dmzj.com/', 'm.dmzj.com/info/').replace('.html',
                                                                                    '') + '.html'  # 发现了新的规律，这个替换把电脑版的替换成手机版的
    url_lists = get_all_urls(url)
    with ThreadPoolExecutor(15) as f:
        for url in url_lists:
            f.submit(main, url)
    print('\n全部下载完毕')
