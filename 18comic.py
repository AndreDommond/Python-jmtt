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
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8') #改变标准输出的默认编码
#公共请求头
public_headers={
   'cookie':'',            #填自己的cookie和user-agent
    'User-Agent':''
}
path = ''                    #替换自己的路径并把\换成/   举例（D:\Adults\漫画\）换成（D:/Adults/漫画/）
path_0= ''                   #替换自己的路径并把\换成/
#大类（分类）链接转换为目录和开始阅读链接
def getData(url):
    request= req.Request(url,headers=public_headers)
    with req.urlopen(request,timeout=20) as response:
        data= response.read().decode('utf-8')
        root= bs4.BeautifulSoup(data, 'html.parser')
        pages= root.find_all('div', class_='thumb-overlay')
        titles= root.find_all('div', class_='thumb-overlay')
        dates= root.find_all('div', class_='video-views pull-left')
        for title,page,date in zip(pages,titles,dates):
            dir_name= page.img['alt']
            date= date.string
            year = re.findall(r'(\w+[0-9])-\w+[0-9]-\w+[0-9]', date)
            month = re.findall(r'\w+[0-9]-(\w+[0-9])-\w+[0-9]', date)
            #day = re.findall(r'\w+[0-9]-\w+[0-9]-(\w+[0-9])', date)
            cover_url= title.img['data-original']
            page_url= re.findall(r'/\w+[a-z]/(\d+[0-9])', cover_url)
            zh= urllib.parse.quote(dir_name)
            pageurl='https://18comic1.one/photo/'+'/'.join(page_url)+ '/'
            cover= 'https://18comic1.one/album/'+'/'.join(page_url)+ '/'+''.join(zh)
            if int(''.join(year))<2021 and int(''.join(month))<11:                      #辨别最新反爬的漫画并调用图片处理函数（这我自己推断的，可能有些不准，但大多数应该可以处理（大概吧。。））
                try:                                              #无需处理的图片链接
                    changed_imgeurl(pageurl)
                    changed_listid(cover)
                except AttributeError:
                    print('漫画'+page.img['alt']+'只有一章哦!')
                    continue
            else:                                                  #需要处理的图片链接
                try:
                    getImageurl(pageurl)
                    listid(cover)
                except AttributeError:
                    print('漫画'+page.img['alt']+'只有一章哦!')
                    continue
        nextlinks= root.find('a', class_='prevnext')
        return nextlinks['href']
#解析出目录和开始阅读的图片链接
def getImageurl(url):
    request= req.Request(url,headers=public_headers)
    with req.urlopen(request,timeout=20) as response:
        data= response.read().decode('utf-8')
        root= bs4.BeautifulSoup(data, 'html.parser')
        imageurls= root.find_all('div', style='text-align:center;')
        imgids= root.find_all('div', style='text-align:center;')
        titles= root.find('div', class_='pull-left hidden')
        opener=req.build_opener()                                        #给urlretrieve函数加上伪装
        opener.addheaders=[('User-Agent','')]                            #填自己的user-gent跟上面一样
        req.install_opener(opener)
        path_2= path_0+titles.string.replace('\n','')
        fonder= os.path.exists(path_2)
        if not fonder:
            os.mkdir(path_2)
        for imageurl,imgid in zip(imageurls,imgids):
            imgurl= imageurl.img['data-original']
            imgid= imageurl.img['id']
            imgid_last= re.findall(r'\w+[a-z]_\w+[a-z]_(\w+[0-9]).', imgid)
            imagid= ''.join(imgid_last)
            path_dw= path_2+'/{title}.jpg'.format(title=imagid)
            print('开始下载{title}.jpg'.format(title=imagid))
            jpgs= req.urlretrieve(imgurl,filename=path_dw,reporthook=loading,data=None)
            print(jpgs)
            convertImg(path_dw)
#无需处理的图片链接
def changed_imgeurl(url):
    request= req.Request(url,headers=public_headers)
    with req.urlopen(request,timeout=20) as response:
        data= response.read().decode('utf-8')
        root= bs4.BeautifulSoup(data, 'html.parser')
        imageurls= root.find_all('div', style='text-align:center;')
        titles= root.find('div', class_='pull-left hidden')
        opener=req.build_opener()
        opener.addheaders=[('User-Agent','')]                             #跟上面一样
        req.install_opener(opener)
        path_1 = path+titles.string.replace('\n','')
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
            jpgs= req.urlretrieve(imgurl,filename=path_dw,reporthook=loading,data=None)
            print(jpgs)
#回调函数
def loading(blocknum, blocksize, totalsize):
    '''回调函数
    blocknum: 已经下载的数据块
    blocksize: 数据块的大小
    totalsize: 远程文件的大小
    '''
    percent= 100.0*blocknum*blocksize/totalsize
    if percent > 100:
        percent= 100
    print("%.2f%%"% percent)                                             #睡眠
    time.sleep(0.5)
#无需处理的解析目录链接后用解析图片的函数（）再解析
def changed_listid(url):
    request= req.Request(url,headers=public_headers)
    with req.urlopen(request,timeout=20) as response:
        data= response.read().decode('utf-8')
        root= bs4.BeautifulSoup(data, 'html.parser')
        contents= root.find('ul', class_='btn-toolbar')          #查找所有ul链接下的目录链接
        for k in contents.find_all('a'):                         #提取所有a标签中的'href'属性，并输出最终开始阅读链接   
            mu_list= 'https://18comic1.one'+k.get('href')
            changed_imgeurl(mu_list)
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
pageurl= input('请输入想获取的分类链接：')                                      #连接类型https://18comic1.one/search/photos?search_query=%E8%BF%91%E8%A6%AA%E4%BA%82%E5%80%AB&page=1类似于这种没有（&page=1）也可以
#控制爬取的页数
count=0
while count<page:
    pageurl=getData(pageurl)
    count+=1
if __name__ == '__main__':
    getData(pageurl)