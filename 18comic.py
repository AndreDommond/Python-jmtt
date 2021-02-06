import io
import sys
import urllib.request as req
import bs4
import re
import PIL.Image
import time
import random
from PIL import Image
import urllib
import os 
import requests
from fake_useragent import UserAgent
from multiprocessing import Pool
import multiprocessing
ua = UserAgent()
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8') #改变标准输出的默认编码
#公共请求头
public_headers={
   'cookie':'__cfduid=d3af1fe4e02395143768f49120192d89a1612161290; _gid=GA1.2.537470263.1612161292; shunt=1; AVS=pgucjspmo4rgafa4vinl3feug4; ipcountry=TW; ipm5=ad96616d894884f20b4e263448a05911; _ga_YYJWNTTJEN=GS1.1.1612339484.9.1.1612339785.59; _gat_ga0=1; _gat_ga1=1; _ga=GA1.2.2093487367.1612161292; _gat_gtag_UA_99252457_3=1; cover=1; _gali=chk_cover',
    'User-Agent':ua.random
}
path = input('请输入无需处理的漫画保存路径：')                #替换自己的路径并把\换成/
#大类（分类）链接转换为目录和开始阅读链接
def getData(url):
    try:
        request= req.Request(url,headers=public_headers)
        with req.urlopen(request,timeout=20) as response:
            data= response.read().decode('utf-8')
            root= bs4.BeautifulSoup(data, 'html.parser')
            pages= root.find_all('div', class_='thumb-overlay')
            titles= root.find_all('div', class_='thumb-overlay')
            dates= root.find_all('div', class_='video-views pull-left')
            response.close()
            for title,page,date in zip(pages,titles,dates):
                dir_name= page.img['alt']
                date= date.string
                year = re.findall(r'(\w+[0-9])-\w+[0-9]-\w+[0-9]', date)
                month = re.findall(r'\w+[0-9]-(\w+[0-9])-\w+[0-9]', date)
                day = re.findall(r'\w+[0-9]-\w+[0-9]-(\w+[0-9])', date)
                cover_url= title.img['data-original']
                page_url= re.findall(r'/\w+[a-z]/(\d+[0-9])', cover_url)
                zh= urllib.parse.quote(dir_name)
                pageurl='https://18comic1.one/photo/'+'/'.join(page_url)+ '/'
                cover= 'https://18comic1.one/album/'+'/'.join(page_url)+ '/'+''.join(zh)
                if int(''.join(year))<2020:
                    try:                                              #无需处理的图片链接
                        changed_imgeurl(pageurl)
                        changed_listid(cover)
                    except AttributeError:
                        print('漫画'+page.img['alt']+'只有一章哦!')
                        continue
                if int(''.join(year))==2020 and int(''.join(month))==10 and int(''.join(day))<27:
                    try:                                              #无需处理的图片链接
                        changed_imgeurl(pageurl)
                        changed_listid(cover)
                    except AttributeError:
                        print('漫画'+page.img['alt']+'只有一章哦!')
                        continue
                if int(''.join(year))==2020 and int(''.join(month))<10:
                    try:                                              #无需处理的图片链接
                        changed_imgeurl(pageurl)
                        changed_listid(cover)
                    except AttributeError:
                        print('漫画'+page.img['alt']+'只有一章哦!')
                        continue
                else:                                                #需要处理的图片链接
                    try:
                        getImageurl(pageurl)
                        listid(cover)
                    except AttributeError:
                        print('漫画'+page.img['alt']+'只有一章哦!')
                        continue
    except urllib.error.URLError:
        print('请求过快，连接关闭！')
        getData(url)
    except ConnectionResetError:
        getData(url)
    except ValueError:
        print('漫画下载完毕')
    try:
        nextlinks= root.find('a', class_='prevnext')
        return nextlinks['href']
    except TypeError:
        print('此页面的漫画下载完成了！')
    except UnboundLocalError:
        print('enjoy！')
#解析出目录和开始阅读的图片链接
def getImageurl(url):
    try:
        request= req.Request(url,headers=public_headers)
        with req.urlopen(request,timeout=20) as response:
            data= response.read().decode('utf-8')
            root= bs4.BeautifulSoup(data, 'html.parser')
            imageurls= root.find_all('div', style='text-align:center;')
            imgids= root.find_all('div', style='text-align:center;')
            titles= root.find('div', class_='pull-left hidden')
            response.close()
            opener=req.build_opener()
            opener.addheaders=[('User-Agent',ua.random)]
            req.install_opener(opener)
            title=titles.string.replace('\n','')
            title = re.sub(r'[/\:*?"<>|]', '' ,title)
            path_1 = path+title.rstrip()
            fonder= os.path.exists(path_1)
            if not fonder:
                os.mkdir(path_1)
            for imageurl,imgid in zip(imageurls,imgids):
                imgurl= imageurl.img['data-original']
                imgid= imageurl.img['id']
                imgid_last= re.findall(r'\w+[a-z]_\w+[a-z]_(\w+[0-9]).', imgid)
                imagid= ''.join(imgid_last)
                path_dw= path_1+'/{title}.jpg'.format(title=imagid)
                print('开始下载{title}.jpg'.format(title=imagid))
                jpgs= req.urlretrieve(imgurl,filename=path_dw)
                print(jpgs)
                convertImg(path_dw)
    except urllib.error.URLError:
        print('请求过快，连接关闭!')
        getImageurl(url)
    except ConnectionResetError:
        getImageurl(url)
#无需处理的图片链接
def changed_imgeurl(url):
    try:
        request= req.Request(url,headers=public_headers)
        with req.urlopen(request,timeout=20) as response:
            data= response.read().decode('utf-8')
            root= bs4.BeautifulSoup(data, 'html.parser')
            imageurls= root.find_all('div', style='text-align:center;')
            titles= root.find('div', class_='pull-left hidden')
            response.close()
            opener=req.build_opener()
            opener.addheaders=[('User-Agent',ua.random)]
            req.install_opener(opener)
            title=titles.string.replace('\n','')
            title = re.sub(r'[/\:*?"<>|]', '' ,title)
            path_1 = path+title.rstrip()
            fonder= os.path.exists(path_1)
            if not fonder:
                os.mkdir(path_1)
            for imageurl in imageurls:
                imgurl= imageurl.img['data-original']
                imgid= imageurl.img['id']
                imgid_last= re.findall(r'\w+[a-z]_\w+[a-z]_(\w+[0-9]).', imgid)
                imagid= ''.join(imgid_last)
                path_dw= path_1+'/{title}.jpg'.format(title=imagid)
                print('开始下载{title}.jpg'.format(title=imagid))
                jpgs= req.urlretrieve(imgurl,filename=path_dw)
                print(jpgs)
    except urllib.error.URLError:
        print('请求过快，连接关闭！')
        changed_imgeurl
    except ConnectionResetError:
        changed_imgeurl
#无需处理的解析目录链接后用解析图片的函数（）再解析
def changed_listid(url):
    request= req.Request(url,headers=public_headers)
    with req.urlopen(request,timeout=20) as response:
        data= response.read().decode('utf-8')
        root= bs4.BeautifulSoup(data, 'html.parser')
        contents= root.find('ul', class_='btn-toolbar')       #查找所有ul链接下的目录链接
        for k in contents.find_all('a'):
            mu_list= 'https://18comic1.one'+k.get('href')
            date_all=k.span.string
            year = re.findall(r'(\w+[0-9])-\w+[0-9]-\w+[0-9]', date_all)
            month = re.findall(r'\w+[0-9]-(\w+[0-9])-\w+[0-9]', date_all)
            day = re.findall(r'\w+[0-9]-\w+[0-9]-(\w+[0-9])', date_all)
            if int(''.join(year))<2020:                                             #无需处理的图片链接
                changed_imgeurl(mu_list)
            if int(''.join(year))==2020 and int(''.join(month))==10 and int(''.join(day))<27:                                           #无需处理的图片链接
                changed_imgeurl(mu_list)
            if int(''.join(year))==2020 and int(''.join(month))<10:                                           #无需处理的图片链接
                changed_imgeurl(mu_list)
            else:                                                #需要处理的图片链接
                getImageurl(mu_list)                   #提取所有a标签中的'href'属性，并输出最终开始阅读链接 
#解析目录链接后用解析图片的函数（）再解析
def listid(url):
    request= req.Request(url,headers=public_headers)
    with req.urlopen(request,timeout=20) as response:
        data= response.read().decode('utf-8')
        root= bs4.BeautifulSoup(data, 'html.parser')
        contents= root.find('ul', class_='btn-toolbar')          #查找所有ul链接下的目录链接
        for k in contents.find_all('a'):                         #提取所有a标签中的'href'属性，并输出最终开始阅读链接   
            mu_list= 'https://18comic1.one'+k.get('href')
            getImageurl(mu_list)                                 #使用解析图片链接进行链接解析
#对反爬图片进行处理
def convertImg(img_url):
    img = Image.open(img_url)
    img_size = img.size
    img_crop_size = int(img_size[1] / 10)
    img_crop_size_last = (img_size[1] / 10) - img_crop_size  # 解决图片height不能被10整除导致拼接后下方黑条
    img_crop_size_last = round(img_crop_size_last, 1)
    if img_crop_size_last > 0:  # 只有无法整除时才将新建图片进行画布纵向减小
        img_crop_size_last_sum = int(img_crop_size_last * 10)
    else:
        img_crop_size_last_sum = 0
    img_width = int(img_size[0])
    img_block_list = [] #定义一个列表用来存切割后图片
    for img_count in range(10):
        img_crop_box = (0, img_crop_size*img_count, img_width, img_crop_size*(img_count+1))
        img_crop_area = img.crop(img_crop_box)
        img_block_list.append(img_crop_area)
    img_new = Image.new('RGB', (img_size[0], img_size[1]-img_crop_size_last_sum))
    count = 0
    for img_block in reversed(img_block_list):
        img_new.paste(img_block, (0, count*img_crop_size))
        count += 1
    #img_new.show() # 调试显示转化后的图片
    img_new.save(img_url)
#需要爬取的页数
page= int(input('请输入想要获取的页数：'))
#需要解析的链接
pageurl= input('请输入想获取的分类链接：')                                                         # https://18comic.vip/search/photos?search_query=%E6%AF%8D%E5%AD%90&page=3 https://18comic1.one/search/photos?search_query=%E6%88%91%E8%A6%81%E6%88%90%E4%B8%BA%E5%8D%83%E9%87%91%E7%8C%8E%E4%BA%BA&main_tag=0
#控制爬取的页数                                                                                   # https://18comic1.one/search/photos?search_query=%E7%81%AB%E5%BD%B1%E5%BF%8D%E8%80%85-%E9%B8%A3%E4%BA%BA%E4%B8%8E%E5%AE%B6%E4%BA%BAV2&main_tag=0
count=0
while count<page:
    pageurl=getData(pageurl)
    count+=1
if __name__ == '__main__':
    getData(pageurl)
