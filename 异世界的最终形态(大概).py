import re
import requests
from concurrent.futures import ThreadPoolExecutor

obj_title = re.compile(r'<title>(?P<title>.*?)第.*?</title>', re.S)
obj_name = re.compile(r'<title>(?P<name>.*?)</title>', re.S)
obj_link = re.compile(r'","link_pre":.*?,"url":"(?P<link>.*?)","url_next":"', re.S)


def mkdir(path):  # 创建文件夹
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


def download(url: str, fname: str, name):
    from tqdm import tqdm
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get('content-length', 0))
    with open(fname, 'wb') as file, tqdm(
            desc=name,
            total=total,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


def pa(url, i):
    global c
    if c == 0:
        ual = url + str(i)
        rest = requests.get(ual)
        rest.encoding = "utf-8"
        title = obj_title.search(rest.text).group("title").replace(":", "").replace("/", "")
        name = obj_name.search(rest.text).group("name").replace(":", "").replace("/", "")
        link = obj_link.search(rest.text).group("link").replace("\/", "/")
        film = "E:/番/" + title
        if len(link) != 0:
            if name.find("PV") == -1 and name.find("SP") == -1:
                mkdir(film)
                if len(name) >= 45:
                    name = "第" + name.split("第")[1]
                video_file = film + '/' + name
                if ".m3u8" in link:
                    video_file = video_file + '.m3u8'
                    download(link, video_file, name)
                    # print(f"{name}.m3u8下载完成")
                elif ".mp4" in link:
                    video_file = video_file + '.mp4'
                    download(link, video_file, name)
                    # print(f"{name}.mp4下载完成")
            else:
                print("这个是pv或者sp，不进行下载")
        else:
            c += 1
        rest.close()


if __name__ == '__main__':
    while 1:
        baseual = input(">>>")
        url = re.sub('/nid/.*', "/nid/", baseual)  # 使用正则转换成普通ual
        t = input("从第几集开始>>>")
        if len(t) == 0:
            t = 1
        else:
            t = int(t)
        c = 0
        with ThreadPoolExecutor(10) as f:
            for i in range(t, 40):
                f.submit(pa, url, i)
