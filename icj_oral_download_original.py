from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
import urllib.request
import random
import requests

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

#写入浏览器的header，伪装成浏览器访问
my_header = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'

#定义获取爬虫403 forbidden网页的函数
def get_content(url,header):
    randdom_header=random.choice(header)
    req=urllib.request.Request(url)
    req.add_header("User-Agent",randdom_header)
    req.add_header("Referer","https://www.icj-cij.org/home")
    req.add_header("GET",url)
    content=urllib.request.urlopen(req).read()
    return content

#爬虫、解析（用html.parser似乎无法成功解析，这里用最强大但慢的html5lib解析器）
url='https://www.icj-cij.org/list-of-all-cases'
new_url = ''
html = get_content(url,my_header)
soup = BeautifulSoup(html, "html5lib")
tags = soup.find_all('a')

#遍历ICJ All Cases网页的源代码
for tag in tags:
    #找到每个case的链接
    link = tag.get('href','not a link')
    if 'case/' in link:
        case_page = 'https://www.icj-cij.org/'+link
        #找出case编号，以备作为文件名
        case_num = link.strip('case/')
        new_url = case_page
        print(f'这是第{case_num}号案件')
        #打开每个case的详情页
        new_html = get_content(new_url,my_header)
        new_soup = BeautifulSoup(new_html, "html5lib")
        new_tags = new_soup.find_all('a')
        #给每个case的口头辩论文件编号，避免重复命名
        i = 0
        #遍历每个case的详情页是否有口头辩论记录
        for new_tag in new_tags:
            if 'Verbatim record' in new_tag.get_text():
                #给每个口头辩论记录命名
                case_name = case_num+'_'+str(i)
                print(case_name)
                #打开每个口头辩论记录的PDF
                case_file = requests.get(new_tag.get('href'))
                print(case_file)
                #将口头辩论记录的PDF以byte形式写入到本地
                with open(f'{case_name}.pdf','wb') as file_object:
                    file_object.write(case_file.content)
                #口头辩论记录编号更新
                i+=1