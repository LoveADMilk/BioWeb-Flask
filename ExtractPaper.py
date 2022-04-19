import time

import pymysql #导入模块
from bs4 import BeautifulSoup               #网页解析，获取数据
import re                                   #正则表达式
import urllib.request,urllib.error          #指定URL，获取数据
from urllib.error import URLError

class MySQL():
    def connect(self):
        '''连接MySQL数据库'''
        try:
            connection = pymysql.connect(
                host='127.0.0.1',
                port=3306,
                user='root',
                passwd='123456',
                db='biowebvirus',
                charset='utf8'
                )
            return connection
        except Exception:
            raise Exception("数据库连接失败")

    def implement(self, data):
        db = self.connect()
        print(data)
        for col in data:
            print(col)
        with db.cursor() as cursor:
            # 创建sql语句 , 对于自增主键只需要用0即可insert插入即可
            sql = "insert into `paper`(`id`, `name`,`author`, `address`, `info`, `year`, `citations`,`pdf`) values (%s, %s, %s, %s, %s, %s, %s, %s)"
            # 执行sql
            cursor.execute(sql, (0, data[0], data[1], data[2], data[3], data[4], data[5], data[6]))
            # 提交
            db.commit()
            db.close()

class Paper():
    def getData(self, start_url, end_url):
        # PDF链接的div
        downLoadFileExist_reg = re.compile(r'<div class="gs_ggs gs_fl">')
        # 完整链接PDF
        downLoadFileLink_reg = re.compile(r'href="(.*?)">')
        # 显示的部分摘要
        content_reg = re.compile(r'<div class="gs_ri">(.*?)<div class="gs_rs">')
        # 文章的链接
        fileLink_reg = re.compile(r'href="(.*?)" id="')
        # 文章标题
        fileName_reg = re.compile(r'<a data-clk="hl=zh-CN&amp;sa=T&amp;ct=res&amp;.*?">(.*?)</a>')
        # 时间与文章的期刊
        periodicalTime_reg = re.compile(r'<div class="gs_a">.*?- (.*?)</div>')
        # 引用次数
        quteNum_reg = re.compile(r'<div class="gs_fl">.*?hl=zh-CN">被引用次数：(.*?)</a>')
        # 每10为1页 ,由于前两页已经完成 爬取所以设置为20开始
        start_num = 0
        # 每10页为1组
        for i in range(0, 10):
            time.sleep(600)  # 休眠600秒，没爬取1页休眠600秒，防止被ban
            datalist = []
            url = start_url + str(start_num) + end_url
            start_num = start_num + 10
            # 返回抓取到的HTML文本
            html = self.askURL(url)
            # 逐一解析
            # BeautifulSoup(html, "html.parser")指定解析器为html.parser
            soup = BeautifulSoup(html, "html.parser")

            #  find_all() 方法的返回结果是值包含一个元素的列表
            # div<class="gs_r gs_or gs_scl"> 该div是包含当前论文信息的最大div
            # 按照Google学术的页面格式,该返回值列表 长度应该是10
            for item in soup.find_all('div', class_="gs_r gs_or gs_scl"):
                data = []
                item_str = str(item)
                # 有可能不存在PDF链接
                if re.findall(downLoadFileExist_reg, item_str) == []:
                    downLoadFilelink = ''
                else:
                    # PDF链接
                    downLoadFilelink = re.findall(downLoadFileLink_reg, item_str)[0]  # re通过正则表达式查找指定的字符串
                # 文章部分内容
                content_str = re.findall(content_reg, item_str)[0]

                fileLink = re.findall(fileLink_reg, content_str)[0]

                fileName1 = re.findall(fileName_reg, content_str)

                # 由于存在HTML格式的文件，所以在此特殊判断，先不对HTML的进行爬取
                if len(fileName1) == 0:
                    # for aName in item.find('h3', class_="gs_rt").find('a'):
                    #     data.append(aName)
                    # print(aName)
                    # print("---")
                    continue
                else:
                    fileName = re.findall(fileName_reg, content_str)[0]

                    fileName = re.sub('<b>', '', fileName)

                    fileName = re.sub('</b>', '', fileName)
                    #     文章名字
                    data.append(fileName)
                    # 获得当前文章的作者，由于有的文章作者是没有a标签的，所以也需要特殊判断
                    if (item.find('div', class_="gs_a").find('a')):
                        for author in item.find('div', class_="gs_a").find('a'):
                            data.append(author)
                    else:
                        for author in item.find('div', class_="gs_a"):
                            # print(author.split(",")[0])
                            data.append(author.split(",")[0])

                periodicalTime = re.findall(periodicalTime_reg, content_str)[0]

                periodicalTime = re.sub('<b>', '', periodicalTime)

                periodicalTime = re.sub('</b>', '', periodicalTime)

                periodicalTime = re.sub('\xa0', '', periodicalTime)

                quteNum = re.findall(quteNum_reg, item_str)

                if len(quteNum) == 0:
                    quteNum = ''
                else:
                    quteNum = quteNum[0]

                # 文章'https://www.mdpi.com/2227-7080/9/1/2'
                data.append(fileLink)
                # 'Technologies, 2020 - mdpi.com'
                data.append(periodicalTime)

                # 从中截取年份
                dateTimePattern = re.compile(r'\d{4}')
                dateTime = dateTimePattern.findall(periodicalTime)
                data.append(dateTime[0])
                # 引用次数
                data.append(quteNum)
                # PDF链接'https://www.mdpi.com/2227-7080/9/1/2/pdf'
                data.append(downLoadFilelink)

                datalist.append(data)

            print("第", start_num % 10 + 1, "页完成")
            print(datalist)
            # 对于datalist的子序列data而言 0列：文章名 ，1：作者，2：文章地址，3：所属期刊信息 4：年份， 5：引用数 6：pdf地址
            for data in datalist:
                mysql = MySQL()
                mysql.implement(data)
            print("第", start_num % 10 + 1, "页存储完成")

        return "OK"

    # 返回抓取到的HTML
    def askURL(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/90.0.4430.93 Safari/537.36'}
        req = urllib.request.Request(url=url, headers=headers)
        try:
            res = urllib.request.urlopen(req, timeout=7)
            html = res.read().decode('utf-8')
        except URLError as e:
            if hasattr(e, "code"):
                print(e.code)
            if hasattr(e, "reason"):
                print(e.reason)
        return html


if __name__ == '__main__':
    start_url="https://scholar.google.com/scholar?start="
    # 搜索关键字是
    # Influenza A virus Antigenic distance deep learning
    end_url = "&q=Influenza+A+virus+Antigenic+distance+deep+learning&hl=zh-CN&as_sdt=0,5"
    mypaper = Paper()
    mypaper.getData(start_url, end_url) # 根据关键词爬取网页并存入数据库












