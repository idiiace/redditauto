# -*- coding: utf-8 -*-


import time

from PyQt5 import QtCore, QtGui, QtWidgets
import random
import threading
from PyQt5.QtCore import pyqtSignal


if hasattr(QtCore.Qt, "AA_EnableHighDpiScaling"):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, "AA_UseHighDpiPixmaps"):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

import sys
import praw
import time
import requests
import json

CONFIG_FILE='config.json'

latest={}
config=''
wait = 30


#________________________________________________________

# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException

from selenium.webdriver.firefox.options import Options
from fake_useragent import UserAgent
import random


class Send_DM:

    def __init__(self):
        
        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
        
        options = Options()
        ua = UserAgent()
        options = Options()
        
        options.headless =True
        #ua = UserAgent()
        userAgent = ua.random
        options.add_argument(f'user-agent={userAgent}')
        #options.add_argument("user-data-dir=selenium")
        #options.add_argument('--window-size=1920,1080')
        #$options.add_argument("--disable-gpu")
        #driver = webdriver.Chrome(chrome_options=options)
        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(30)
        self.logged_in =False


    def login_to_reddit(self,username=False,password=False):
        
        driver = self.driver
        driver.get("https://www.reddit.com/chat")
        try:
            driver.find_element_by_id("loginPassword").clear()
            driver.find_element_by_id("loginPassword").send_keys(f"{password}")
            driver.find_element_by_id("loginUsername").clear()
            driver.find_element_by_id("loginUsername").send_keys(f"{username}")
            driver.find_element_by_xpath("//button[@type='submit']").click()
        except:
            pass
        self.logged_in =True
        
    def send_message(self,user,message):
        
        if self.logged_in:
            try:
                driver = self.driver
                user=user
                #Kires952
                driver.get('https://www.reddit.com/chat/channel/create')
                
                driver.find_element_by_xpath('//*[@id="tooltip-container"]/form/div/div[1]/div[2]/span[2]/input').send_keys(f'{user}')
                time.sleep(3)
                driver.find_element_by_xpath('//*[@id="tooltip-container"]/form/div/div[1]/div[3]/div[2]').click()
                driver.find_element_by_xpath('//*[@id="tooltip-container"]/form/div/div[2]/button[2]').click()
                time.sleep(1)
                driver.find_element_by_xpath('//*[@id="MessageInputTooltip--Container"]/div/div/textarea').send_keys(message)
                time.sleep(1)
                driver.find_element_by_xpath("//form[@id='MessageInputTooltip--Container']/div/div/textarea").send_keys(u'\ue007')
                return True
            except Exception as e:
                return False



#________________________________________________________

def all_subreddits(r):
    f=r.user.subreddits(limit=None)
    a=[x.display_name for x in f]
    return a

def open_browser():        
    webbrowser.open(latest['url'])
    

def notify_windows(a,b,c):
    global latest

    if 'task' in b.lower():
        #print ('Found ')
        notif_ = ToastNotifier()
        latest['title']=b
        latest['url']=c
        #f=open('urls.txt','a').write(c)
        f=open('urls.txt').read()
        do = False
        for i in f.splitlines():
            if i ==c:
                do = True
                
        if do == True:
            pass
        else:
            f=open('urls.txt','a').write('\n')
            f=open('urls.txt','a').write(c)
            notif_.show_toast("Tasks slaveLabour",latest['title'],
            duration=5,icon_path="icon.ico",callback_on_click=open_browser)

def handle_post(submission):
    #print('called')
    url = submission.shortlink
    title = submission.title
    sub = submission.subreddit.display_name
    #print(submission.author)
    #print(url,title,sub)

    if config['keywords']['enabled']:
        if any(x.lower() in title.lower() for x in config['keywords']['list']):
            notify(sub, title, url)
    else:
        notify(sub, title, url)

def handle_modqueue(item):
    url = 'https://reddit.com' + item.permalink
    sub = item.subreddit.display_name
    notify(sub, 'Modqueue', url)
    #print(item.subreddit.display_name)

def notify(subreddit, title, url):
    if first: return
    if config['discord']['enabled']:
        notify_discord(subreddit, title, url)
    if config['slack']['enabled']:
        notify_slack(subreddit, title, url)
    if config['reddit_pm']['enabled']:
        notify_reddit(subreddit, title, url)
    if config['telegram']['enabled']:
        notify_telegram(subreddit, title, url)
    if config['windows']['enabled']:
        notify_windows(subreddit, title, url)
    if config['debug']:
        print(subreddit + ' | ' + title + ' | ' +  url)

def notify_discord(subreddit, title, url):
    message = title + " | <" + url + ">"
    payload = { 'content': message }
    headers = { 'Content-Type': 'application/json', }
    requests.post(config['discord']['webhook'], data=json.dumps(payload), headers=headers)

def notify_slack(subreddit, title, url):
    message = title + " | " + url
    payload = { 'text': message }
    headers = { 'Content-Type': 'application/json', }
    requests.post(config['slack']['webhook'], data=json.dumps(payload), headers=headers)

def notify_reddit(subreddit, title, url):
    if title == 'Modqueue':
        subject = 'New item in modqueue on /r/' + subreddit + '!'
    else:
        subject = 'New post on /r/' + subreddit + '!'

    message = '[' + title + '](' + url + ')'

    for user in config['reddit_pm']['users']:
        r.redditor(user).message(subject, message)

def notify_telegram(subreddit, title, url):
    message = '<b>[/r/{}]</b> {} - {}'.format(subreddit, title, url)
    payload = {
        'chat_id': config['telegram']['chat_id'],
        'text': message,
        'parse_mode': 'HTML'
    }
    requests.post("https://api.telegram.org/bot{}/sendMessage".format(config['telegram']['token']),
                  data=payload)

def start_streams():
            
    subreddits = '+'.join(config['subreddits'])
    modqueue_stream = (r.subreddit('mod').mod.stream.modqueue(pause_after=-1)
                       if config['modqueue'] else [])
    submission_stream = (r.subreddit(subreddits).stream.submissions(pause_after=-1)
                         if config['new_posts'] else [])
    return modqueue_stream, submission_stream


class Ui_Dialog(object):
    
    def setupUi(self, Dialog,title="Reddit Bot"):
        
        self.logged_in=False
        self.messages_to_send=[]
        Dialog.setObjectName("Dialog")
        Dialog.resize(516, 390)
        self.columnView = QtWidgets.QColumnView(Dialog)
        self.columnView.setGeometry(QtCore.QRect(10, 10, 491, 101))
        self.columnView.setObjectName("columnView")
        self.username = QtWidgets.QPlainTextEdit(Dialog)
        self.username.setGeometry(QtCore.QRect(20, 20, 131, 31))
        self.username.setObjectName("username")
        self.password = QtWidgets.QPlainTextEdit(Dialog)
        self.password.setGeometry(QtCore.QRect(160, 20, 151, 31))
        self.password.setObjectName("password")
        self.LoginButton = QtWidgets.QPushButton(Dialog)
        self.LoginButton.setGeometry(QtCore.QRect(330, 10, 171, 101))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.LoginButton.setFont(font)
        self.LoginButton.setObjectName("LoginButton")
        self.client_id = QtWidgets.QPlainTextEdit(Dialog)
        self.client_id.setGeometry(QtCore.QRect(20, 60, 131, 31))
        self.client_id.setObjectName("client_id")
        self.client_secret = QtWidgets.QPlainTextEdit(Dialog)
        self.client_secret.setGeometry(QtCore.QRect(160, 60, 151, 31))
        self.client_secret.setObjectName("client_secret")
        self.columnView_2 = QtWidgets.QColumnView(Dialog)
        self.columnView_2.setGeometry(QtCore.QRect(10, 120, 141, 241))
        self.columnView_2.setObjectName("columnView_2")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20, 130, 81, 16))
        self.label.setObjectName("label")
        self.posts = QtWidgets.QTextBrowser(Dialog)
        self.posts.setGeometry(QtCore.QRect(160, 120, 191, 241))
        self.posts.setObjectName("posts")
        self.columnView_3 = QtWidgets.QColumnView(Dialog)
        self.columnView_3.setGeometry(QtCore.QRect(360, 120, 141, 241))
        self.columnView_3.setObjectName("columnView_3")
        self.subreddits = QtWidgets.QListWidget(Dialog)
        self.subreddits.setGeometry(QtCore.QRect(20, 150, 121, 201))
        self.subreddits.setObjectName("subreddits")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(20, 370, 91, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(130, 370, 141, 16))
        self.label_3.setObjectName("label_3")
        self.dmsent = QtWidgets.QTextBrowser(Dialog)
        self.dmsent.setGeometry(QtCore.QRect(370, 150, 121, 201))
        self.dmsent.setObjectName("dmsent")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(370, 130, 81, 16))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(410, 370, 47, 14))
        self.label_5.setObjectName("label_5")
        self.status = QtWidgets.QLabel(Dialog)
        self.status.setGeometry(QtCore.QRect(450, 370, 47, 14))
        self.status.setObjectName("status")
        self.LoginButton.clicked.connect(self.lo)
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        
        self.checkThreadTimer = QtCore.QTimer(Dialog)
        self.checkThreadTimer.setInterval(500) #.5 seconds
        self.not_sending = False
        self.dm=[]
        self.postss=[]
        self.checkThreadTimer.timeout.connect(self.update_gui_values)
        self.checkThreadTimer.start()
        self.wait =30
        
    def update_gui_values(self):
        
        for i in self.postss:
            
            self.posts.append(i)
        self.postss=[]
            
        for i in self.dm:
            self.dmsent.append(i)
        self.dm=[]
        
        if self.not_sending == False:
            
            if self.logged_in ==True:
                x=threading.Thread(target=self.send_timer)
                x.start()
                self.not_sending = True
                
            
    def set_logins(self):
        #self.username.setText()
        
        with open(CONFIG_FILE) as config_file:
            config = json.load(config_file)
        
        self.client_id.setPlainText(config['reddit']['client_id'])
        self.client_secret.setPlainText (config['reddit']['client_secret'])
        self.username.setPlainText(config['reddit']['username'])
        self.password.setPlainText(config['reddit']['password'])

        
    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "RedditBot"))
        self.username.setPlainText(_translate("Dialog", "Username"))
        self.LoginButton.setText(_translate("Dialog", "LOGIN"))
        self.client_id.setPlainText(_translate("Dialog", "Client Id"))
        self.client_secret.setPlainText(_translate("Dialog", "Client Secret"))
        self.label.setText(_translate("Dialog", "SUBREDDITS"))
        self.posts.setHtml(
            _translate(
                "Reddit Bot",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:7.875pt; font-weight:400; font-style:normal;\">\n"
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" color:#aa0000;">R/</span> : </p></body></html>',
            )
        )
        self.label_2.setText(_translate("Dialog", "DM Messages File"))
        self.label_3.setText(_translate("Dialog", "FILE : message.txt"))
        self.dmsent.setHtml(
            _translate(
                "Dialog",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:7.875pt; font-weight:400; font-style:normal;\">\n"
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" color:#aa0000;"></span> : </p></body></html>',
            )
        )
        self.label_4.setText(_translate("Dialog", "DM'S sent "))
        self.label_5.setText(_translate("Dialog", "Status"))
        self.status.setText(_translate("Dialog", "Offline"))
        #self.LoginButton.clicked.connect(self.login())
        self.set_logins()
        
    def lo(self):

        #time.sleep(1)
        self.LoginButton.setText('One Sec')
        self.LoginButton.setEnabled(False)
        self.LoginButton.setText('Successful')
        #get the logins
        #
        username =self.username.toPlainText()
        password =self.password.toPlainText()
        client_id =self.client_id.toPlainText()
        client_secret =self.client_secret.toPlainText()
        
        with open(CONFIG_FILE) as config_file:
            config = json.load(config_file)
            
        config['reddit']['client_id']=client_id
        config['reddit']['client_secret']=client_secret
        config['reddit']['username']=username
        config['reddit']['password']=password
        
        r = praw.Reddit(
            user_agent = config['reddit']['user_agent'],
            client_id = config['reddit']['client_id'],
            client_secret = config['reddit']['client_secret'],
            username = config['reddit']['username'],
            password = config['reddit']['password']
        )
        
        subreddits = all_subreddits(r)
        config['subreddits']= subreddits
        for i in subreddits:
            self.subreddits.addItem(i)
            #print('added')
            self.status.setText('Online')
            self.logged_in=True
        open(CONFIG_FILE,'w').write(json.dumps(config))
        
        
        
        
        #print('Here')
        #print (all_subreddits(r))
        
        
        global_var = globals()
        global_var['config']=config
        global_var['first']=True
        global_var['r']=r
        
        (modqueue_stream, submission_stream) = start_streams()
        
        def background():
            while True:
                try:
                    for item in modqueue_stream:
                        if item is None:
                            break
                        #print ('Item')
                        handle_modqueue(item)
                    
                    for submission in submission_stream:
                        if submission is None:
                            break
                        try:
                            self.handle_post(submission)
                        except:pass
                        #print ('Found')

                    first = False
                    time.sleep(1)
                except:
                    print("stopping for a 30 seconds")
                    time.sleep(30)
        
        
        x=threading.Thread(target=background)
        x.start()

    def send_timer(self):
        #print ("send_timer")
        g = globals()
        g['wait']=24
        
        reddit_dm=Send_DM()
        reddit_dm.login_to_reddit(config['reddit']['username'],config['reddit']['password'])
        
        while True:
            if self.wait == 0:
                try:
                    
                    author,title=self.messages_to_send.pop()
                    #r.redditor(str(author)).message(title, self.get_message())
                    
                    response =reddit_dm.send_message(str(author),self.get_message())
                    if response==True:
                        
                        open('logs.txt','a').write(time.ctime()+'|'+str(author)+'|'+ str(title)+' \n')
                        print('sending',' ',author,' ',title)
                        self.dm.append('<span style=" color:#aa0000;">R/{}</span>'.format(author))

                        self.wait = 24
                    else:
                        print('sending dm failed')
                        
                except Exception as e:
                    self.wait = 24
                    print(e)
            else:
                self.wait -=1
                time.sleep(1)
                #print(self.wait)

            
    def handle_post(self,submission):
        
        #print('called')
        
        url = submission.shortlink
        title = submission.title
        sub = submission.subreddit.display_name
        author=submission.author
        
        #print(url,title,sub)
        open('urls.txt','a').write("\n")
        #print ("called")

        Found = False
        for i in open('urls.txt').read().splitlines():
            if i==url:
                Found==True
        if Found == True: pass
        
        else:
            self.postss.append('<span style=" color:#aa0000;">R/{}</span> :{}'.format(sub,title))
            
            def send_message(author,title):
                            
                '''except Exception as e:
                print(e)
                open('logs.txt','a').write(time.ctime()+' '+str(e)+' \n')
                self.postss.append('<span style=" color:#aa0000;">Error : </span> :{}'.format(e))'''
                    
                           
                the_first = False
                
                self.messages_to_send.append([author,title])
                
                #print(self.message_to_send)
                
                '''if the_first == False:
                    d=threading.Thread(target=send_timer ,args=())
                    d.start()
                    the_first = True'''
                
                
        #print('here')
        
            send_message(author,title)
            #print('started')
            open('urls.txt','a').write(url)
        
            
        #self.dm.append('<span style=" color:#aa0000;">R/{}</span>'.format(author))

        
    def get_message(self):
        
        v=open('message.txt','r').read()
        c=v.splitlines()
        return random.choice(c)

#3KtGr7VDn5QKH7BY6YKhnxXeXGSJV2hdvb

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Breeze")
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

