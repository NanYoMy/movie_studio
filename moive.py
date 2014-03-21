# -*- coding: utf-8 -*- 
import hashlib, urllib, urllib2, re, time, json
import cookielib,string
import xml.etree.ElementTree as ET
from flask import Flask, request, render_template
import MySQLdb
import sae.const
import pylibmc
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8') 

app = Flask(__name__)
app.debug = True

HELP_INFO = \
u"""
欢迎使用幕微^_^

发布最新电影信息，影院排片信息，经典电影

回复1,查看最新电影
回复2,查看经典电影
回复3,查看最热上映电影
回复4,查看即将上映电影
回复5,查看最新影评
回复6,查看最受欢迎影评
回复7,查看影院信息
回复?,查看帮助
"""

#定时更新数据库
@app.route('/updateHotestMovie',methods=['GET','POST'])
def updateHotestMovie():
    opener = getOpener()
    downloadHotestMovie(r"http://theater.mtime.com/China_Shanxi_Province_Xian/movie/",opener)
    return render_template('index.html')

@app.route('/updateLatestMovie',methods=['GET','POST'])
def updateLatestMovie():
    opener = getOpener()
    downloadLatestMovie(r"http://movie.mtime.com/new/",opener)
    return render_template('index.html')

@app.route('/updateLatestMovieReview',methods=['GET','POST'])
def updateLatestMovieReview():
    opener = getOpener()
    downloadLatestMovieReview(r"http://movie.douban.com/review/latest/",opener)
    return render_template('index.html')

@app.route('/updateComingMovie',methods=['GET','POST'])
def updateComingMovie():
    opener = getOpener()
    downloadComingMovie(r"http://movie.douban.com/later/xian/",opener)
    return render_template('index.html')

@app.route('/updateBestMovieReview',methods=['GET','POST'])
def updateBestMovieReview():
    opener = getOpener()
    downloadBestMovieReview(r"http://movie.douban.com/review/best/",opener)
    return render_template('index.html')

@app.route('/updateCinema',methods=['GET','POST'])
def updateCinema():
    #opener = getOpener()
    #downloadcinema(r"http://theater.mtime.com/China_Shanxi_Province_Xian/movie/149778/",opener)
    return render_template('index.html')

@app.route('/updateBestMovie',methods=['GET','POST'])
def updateBestMovie():
    #opener = getOpener()
    #downloadBestMovie(opener)
    return render_template('index.html')

def makeURL(startPosition):
    front='http://movie.douban.com/top250?start='
    end='&filter=&format='
    return front+str(startPosition)+end

def downloadBestMovie(opener):
    sql = 'truncate bestMovie'
    database_execute(sql)

    for i in range(0,10):
       url=makeURL(i*25)
       downloadOnePageBestMovie(url,opener,i*25)

def downloadOnePageBestMovie(web,opener,shift):
    #访问网页
    raw_html =opener.open(web).read()
    #print raw_html
    
    divClass1=re.compile(r'(<div class="grid-16-8 clearfix">)(.+?)(</div>)',re.DOTALL)

    titleAndurlAndImage=re.compile(r'(<a href=")(.+?)("><img alt=")(.+?)(" src=")(.+?)("></a>)')
	
    i=shift
    imageDatabase=""
    titleDatabase=""
    urlDatabase=""	
	
    for titleAndurlAndImageData in titleAndurlAndImage.findall(raw_html):
	urlDatabase=titleAndurlAndImageData[1]
        titleDatabase=titleAndurlAndImageData[3]
        imageDatabase=titleAndurlAndImageData[5]
	sql = "insert into bestMovie values('%s','%s','%s','%s','%s')"%(i,titleDatabase,"",urlDatabase,imageDatabase)
	database_execute(sql)
	i=i+1
        
			
def downloadBestMovieReview(web,opener):
	
    raw_html =opener.open(web).read()
    ul=re.compile(r'(<ul class="tlst clearfix" style="clear:both">)(.+?)(</ul>)',re.DOTALL)

    urlAndtitle=re.compile(r'(<a title=")(.+?)(" href=")(.+?)(" onclick="moreurl)')
    image=re.compile(r'(<img class="fil" src=")(.+?)(" alt=")')    
    
    sql = 'truncate bestMovieReview'
    database_execute(sql)

    i=1    
    for source in ul.findall(raw_html,re.MULTILINE):
        result=source[1]

	urlDatabase=""
	titleDatabase=""
	imageDatabase=""
        for urlAndtitleData in urlAndtitle.findall(result,re.MULTILINE):
            titleDatabase=urlAndtitleData[1]
            urlDatabase=urlAndtitleData[3]
        for imageData in image.findall(result,re.MULTILINE):
            imageDatabase=imageData[1]
            
	sql = "insert into bestMovieReview values('%s','%s','%s','%s','%s')"%(i,titleDatabase,"",urlDatabase,imageDatabase)
        database_execute(sql)
	i=i+1

def downloadLatestMovieReview(web,opener):
	
    raw_html =opener.open(web).read()
    ul=re.compile(r'(<ul class="tlst clearfix" style="clear:both">)(.+?)(</ul>)',re.DOTALL)

    urlAndtitle=re.compile(r'(<a title=")(.+?)(" href=")(.+?)(" onclick="moreurl)')
    image=re.compile(r'(<img class="fil" src=")(.+?)(" alt=")')    
    
    sql = 'truncate latestMovieReview'
    database_execute(sql)

    i=1    
    for source in ul.findall(raw_html,re.MULTILINE):
        result=source[1]

	urlDatabase=""
	titleDatabase=""
	imageDatabase=""
        for urlAndtitleData in urlAndtitle.findall(result,re.MULTILINE):
            titleDatabase=urlAndtitleData[1]
            urlDatabase=urlAndtitleData[3]
        for imageData in image.findall(result,re.MULTILINE):
            imageDatabase=imageData[1]	
	sql = "insert into latestMovieReview values('%s','%s','%s','%s','%s')"%(i,titleDatabase,"",urlDatabase,imageDatabase)
        database_execute(sql)
	i=i+1


def downloadComingMovie(web,opener):
	  #访问网页
    raw_html =opener.open(web).read()
    #print raw_html
    #pattern1 = re.compile(r"(<div class=\"cover\"><a href=\")(.+?)(\"><img src=\")(.+?)(\" /></a></div>)")
    divClass1=re.compile(r'(<div class="item mod ">)(.+?)(</div>)',re.DOTALL)
    divClass2=re.compile(r'(<div class="item mod odd">)(.+?)(</div>)',re.DOTALL)

    urlAndImage=re.compile(r'(<a class="thumb" href=")(.+?)("><img src=")(.+?)(" alt="" /></a>)')
    title=re.compile(r'(<h3><a href=")(.+?)(">)(.+?)(</a><span class="icon">)')    
        
    sql = 'truncate comingMovie'
    database_execute(sql)

    i=1    
    for source in divClass1.findall(raw_html,re.MULTILINE):
        result=source[1]
        
	urlDatabase=""
	imageDatabase=""
	titleDatabase=""

        for urlImageData in urlAndImage.findall(result):
            
	    urlDatabase=urlImageData[1]
            imageDatabase=urlImageData[3]

        for titleData in title.findall(result):
            titleDatabase=titleData[3]
        sql = "insert into comingMovie values('%s','%s','%s','%s','%s')"%(i,titleDatabase,"",urlDatabase,imageDatabase)
        database_execute(sql)
	i=i+1
        
        
    j=i
    for source in divClass2.findall(raw_html,re.MULTILINE):
        result=source[1]	
        urlDatabase=""
	imageDatabase=""
	titleDatabase=""

        for urlImageData in urlAndImage.findall(result):
            
	    urlDatabase=urlImageData[1]
            imageDatabase=urlImageData[3]

        for titleData in title.findall(result):
            titleDatabase=titleData[3]

        sql = "insert into comingMovie values('%s','%s','%s','%s','%s')"%(j,titleDatabase,"",urlDatabase,imageDatabase)
        database_execute(sql)
	j=j+1
	
def downloadHotestMovie(web,opener):
	 #访问网页
    raw_html =opener.open(web).read()
    divClass=re.compile(r'(<ul id="hotplayRegion">)(.+?)(</ul>)')
    divRing=re.compile(r'(<div class="i_ringimg" style="margin:0;">)(.+?)(</div>)')
    for source in divClass.findall(raw_html):
        result=source[1]

    conten=re.compile(r'(<a href=")(.+?)(</a>)')
    urlandtitle=re.compile(r'(<a href=")(.+?)(" target="_blank" title=")(.+?)("><img width="96" height="128" src=")(.+?)(" alt=)')

    sql = 'truncate hotestMovie'
    database_execute(sql)    

    i=1
    for href in divRing.findall(result):
        result1= href[1]
        for data in conten.findall(result1):
            result2=data[0]+data[1]
            for data2  in urlandtitle.findall(result2):
		sql = "insert into hotestMovie values('%s','%s','%s','%s','%s')"%(i,data2[3],"",data2[1],data2[5])
                database_execute(sql)
		i=i+1

def getOpener():

    try:
        #获得一个cookieJar实例
        cj = cookielib.CookieJar()
        #cookieJar作为参数，获得一个opener的实例
        opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        #伪装成一个正常的浏览器，避免有些web服务器拒绝访问。
        opener.addheaders = [('User-agent','Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')]
        return opener
    except Exception,e:
        print str(e)
          
def downloadLatestMovie(web,opener):

    #访问网页
    raw_html =opener.open(web).read()
    #print raw_html
    #pattern1 = re.compile(r"(<div class=\"cover\"><a href=\")(.+?)(\"><img src=\")(.+?)(\" /></a></div>)")
    divClass=re.compile(r"(<ul class=\"showing_list\")(.+?)(</ul>)")
    
    for source in divClass.findall(raw_html):
        result=source[1]
    titleANDurl=re.compile(r'(<div class="item_l"> <p><a href=")(.+?)(/" target="_blank" title=")(.+?)("> <img class="img_box" src=")(.+?)(" width="96" height="128")')
  
    sql = 'truncate lastestMovie'
    database_execute(sql)
    
    i = 1
    for source in titleANDurl.findall(result):

        value = [i,source[3],'des',source[1],source[5]]
        sql = "insert into lastestMovie values('%s','%s','%s','%s','%s')"%(value[0],value[1],value[2],value[3],value[4])
        database_execute(sql)
        i = i+1
        
def downloadcinema(web,opener):

    raw_html =opener.open(web).read()
    dd=re.compile(r"(<dd districtid)(.+?)(</dd>)")
    districs=re.compile(r'(<a class=\\")(.+?)(href=\\")(.+?)(\\")(.+?)(title=\\")(.+?)(\\"><img src=\\")(.+?)(\\" alt=)(.+?)(</a>)')

    sql = 'truncate cinema'
    database_execute(sql)

    i = 1
    for data in dd.findall(raw_html):
        subdata=data[1]
        #print "getdata"
        for source in districs.findall(subdata):
            value = [i,source[7],'des',source[3],source[9]]
            sql = "insert into cinema values('%s','%s','%s','%s','%s')"%(value[0],value[1],value[2],value[3],value[4])
            database_execute(sql)
            i = i+1

            
#homepage just for fun
@app.route('/')
def home():

    '''
    sql = 'create table bestMovieReview(id int primary key , title varchar(1024),description varchar(1024),url varchar(1024),img varchar(1024))'
    database_execute(sql)
    
    sql = 'create table latestMovieReview(id int primary key, title varchar(1024),description varchar(1024),url varchar(1024),img varchar(1024))'
    database_execute(sql)
    sql = 'create table comingMovie(id int primary key, title varchar(1024),description varchar(1024),url varchar(1024),img varchar(1024))'
    database_execute(sql)
    sql = 'create table hotestMovie(id int primary key, title varchar(1024),description varchar(1024),url varchar(1024),img varchar(1024))'
    database_execute(sql)
    sql = 'create table lastestMovie(id int primary key, title varchar(1024),description varchar(1024),url varchar(1024),img varchar(1024))'
    database_execute(sql)
    sql = 'create table bestMovie(id int primary key, title varchar(1024),description varchar(1024),url varchar(1024),img varchar(1024))'
    database_execute(sql)
    sql = 'create table cinema (id int primary key, title varchar(1024),description varchar(1024),url varchar(1024),img varchar(1024))'
    database_execute(sql)
    '''
    #opener = getOpener()
    '''
    sql = 'select * from bestMovieReview order by rand() limit 0,9'
    result = database_execute(sql)

    message = ''
    for record in result:
        temp = record[1]
        a=temp.decode('UTF-8').encode('GBK')[0:60]
        temp=a.decode('GBK').encode('UTF-8')
        #if len(temp) > 100:
        #   temp = temp[0:100]
        message =  message + str(len(temp)) + temp + "! "
    return message
    '''
    #downloadLatestMovie(r"http://movie.mtime.com/new/",opener)
    #downloadHotestMovie(r"http://theater.mtime.com/China_Shanxi_Province_Xian/movie/",opener)
    #downloadBestMovieReview(r"http://movie.douban.com/review/best/",opener)
    #downloadLatestMovieReview(r"http://movie.douban.com/review/latest/",opener)
    #downloadComingMovie(r"http://movie.douban.com/later/xian/",opener)
    #downloadBestMovie(opener)
    #downloadcinema(r"http://theater.mtime.com/China_Shanxi_Province_Xian/movie/149778/",opener)
    
    return render_template('index.html')
    
@app.route('/weixin', methods=['GET','POST'])
def weixin_access_verify():
    echostr = request.args.get('echostr')
    if verification(request) and echostr is not None:
        return echostr
    return 'access verification fail'

@app.route('/', methods=['POST'])
def weixin_msg():

    if verification(request):
        data = request.data
        msg = parse_msg(data)
        if user_subscribe_event(msg):
            return help_info(msg)
        elif is_text_msg(msg):
            content = msg['Content']
            if content == u'1':
                result = get_lastest()
                label = '最新电影'
                rmsg = response_news_msg(msg, result, label)
                return rmsg
            elif content == u'2':
                result = get_bestMovie()
                label = '经典电影'
                rmsg = response_news_msg(msg, result, label)
                return rmsg
            elif content == u'3':
                result = get_hotest()
                label = '最热上映电影'
                rmsg = response_news_msg(msg, result, label)
                return rmsg
            elif content == u'4':
                result = get_coming()
                label = '即将上映电影'
                rmsg = response_news_msg(msg, result, label)
                return rmsg
            elif content == u'5':
                result = get_latestMovieReview()
                label = '最新影评'
                rmsg = response_news_msg(msg, result, label)
                return rmsg
            elif content == u'6':
                result = get_bestMovieReview()
                label = '最受欢迎影评'
                rmsg = response_news_msg(msg, result, label)
                return rmsg
            elif content == u'7':
                result = get_cinema()
                label = '影院信息'
                rmsg = response_news_msg(msg, result, label)
                return rmsg
            else :
                return help_info(msg)

    return 'message processing fail'

def verification(request):
    signature = request.args.get('signature')
    timestamp = request.args.get('timestamp')
    nonce = request.args.get('nonce')

    token = 'movie' #注意要与微信公众帐号平台上填写一致
    tmplist = [token, timestamp, nonce]
    tmplist.sort()
    tmpstr = ''.join(tmplist)
    hashstr = hashlib.sha1(tmpstr).hexdigest()

    if hashstr == signature:
        return True
    return False


#消息解析
def parse_msg(rawmsgstr):
    root = ET.fromstring(rawmsgstr)
    msg = {}
    for child in root:
        msg[child.tag] = child.text
    return msg

def is_text_msg(msg):
    return msg['MsgType'] == 'text'

def user_subscribe_event(msg):
    return msg['MsgType'] == 'event' and msg['Event'] == 'subscribe'

#数据库连接
def database_execute(sql):

    conn=MySQLdb.connect(host=sae.const.MYSQL_HOST,user=sae.const.MYSQL_USER,
                         passwd=sae.const.MYSQL_PASS,db =sae.const.MYSQL_DB,port=int(sae.const.MYSQL_PORT))
   
    cur=conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    cur.close()
    conn.close()  
    return result


def help_info(msg):
    return response_text_msg(msg, HELP_INFO)

#回复文本消息
TEXT_MSG_TPL = \
u"""
<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[%s]]></Content>
<FuncFlag>0</FuncFlag>
</xml>
"""

def response_text_msg(msg, content):
    s = TEXT_MSG_TPL % (msg['FromUserName'], msg['ToUserName'], 
        str(int(time.time())), content)
    return s


#回复图文消息
NEWS_MSG_HEADER_TPL = \
u"""
<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[news]]></MsgType>
<Content><![CDATA[]]></Content>
<ArticleCount>%d</ArticleCount>
<Articles>
"""

NEWS_MSG_TAIL = \
u"""
</Articles>
<FuncFlag>1</FuncFlag>
</xml>
"""
def response_news_msg(recvmsg, result, label):
    msgHeader = NEWS_MSG_HEADER_TPL % (recvmsg['FromUserName'], recvmsg['ToUserName'], 
        str(int(time.time())), len(result))
    msg = ''
    msg += msgHeader
    msg += make_top(label)
    msg += make_items(result)
    msg += NEWS_MSG_TAIL
    return msg

NEWS_MSG_ITEM_TPL = \
u"""
<item>
    <Title><![CDATA[%s]]></Title>
    <Description><![CDATA[%s]]></Description>
    <PicUrl><![CDATA[%s]]></PicUrl>
    <Url><![CDATA[%s]]></Url>
</item>
"""
def make_top(label):
    msg = ''
    title = label
    description = ''
    
    if label == '最新电影': 
        Url = 'http://movie.mtime.com/new/'
        picUrl = 'http://moviestudio.sinaapp.com/static/topPic.jpg'
    elif label == '影院信息':
        Url = 'http://theater.mtime.com/China_Shanxi_Province_Xian/cinema/'
        picUrl = 'http://moviestudio.sinaapp.com/static/cinema.jpg'
    elif label == '最热上映电影':
        Url = 'http://theater.mtime.com/China_Shanxi_Province_Xian/movie/'
        picUrl = 'http://moviestudio.sinaapp.com/static/hotestMovie.jpg'
    elif label == '即将上映电影':
        Url = 'http://movie.douban.com/later/xian/'
        picUrl = 'http://moviestudio.sinaapp.com/static/comingMovie.jpg'
    elif label == '最新影评':
        Url = 'http://movie.douban.com/review/latest/'
        picUrl = 'http://moviestudio.sinaapp.com/static/latestMovieReview.jpg'
    elif label == '最受欢迎影评':
        Url = 'http://movie.douban.com/review/best/'
        picUrl = 'http://moviestudio.sinaapp.com/static/bestMovieReview.jpg'
    elif label == '经典电影':
        Url = 'http://movie.douban.com/top250?start=125&filter=&format='
        picUrl = 'http://moviestudio.sinaapp.com/static/bestMovie.jpg'
    
    msg +=  NEWS_MSG_ITEM_TPL %(title,description,picUrl,Url)
    return msg

def make_items(result):
    msg = ''
    for record in result:
        temp = record[1]
        if len(temp) >90:
            subtemp=temp.decode('UTF-8').encode('GBK')[0:90]
            temp=subtemp.decode('GBK').encode('UTF-8')
        
        title = temp
        description = record[2]
        Url = record[3]
        picUrl = record[4]
        msg +=  NEWS_MSG_ITEM_TPL %(title,description,picUrl,Url)
    return msg

#查询最新电影   
def get_lastest():
    sql = 'select * from lastestMovie order by rand() limit 0,9'
    result = database_execute(sql)
    return result

#查询影院信息
def get_cinema():
    sql = 'select * from cinema order by rand() limit 0,9'
    result = database_execute(sql)
    return result

def get_hotest():
    sql = 'select * from hotestMovie order by rand() limit 0,9'
    result = database_execute(sql)
    return result

def get_coming():
    sql = 'select * from comingMovie order by rand() limit 0,9'
    result = database_execute(sql)
    return result

def get_latestMovieReview():
    sql = 'select * from latestMovieReview order by rand() limit 0,9'
    result = database_execute(sql)
    return result

def get_bestMovieReview():
    #bestMovieReview
    sql = 'select * from bestMovieReview order by rand() limit 0,9'
    result = database_execute(sql)
    return result

def get_bestMovie():
    sql = 'select * from bestMovie order by rand() limit 0,9'
    result = database_execute(sql)
    return result

if __name__ == '__main__':
    app.run()
