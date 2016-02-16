# -*- coding : utf-8 -*-

# Author: Kevin
# Email: testcn@msn.com
# Version: v1.0

import smtplib
from email.mime.multipart import MIMEMultipart
from email.MIMEBase import MIMEBase
import email.MIMEText
import time
import os
from optparse import OptionParser


# parameters process
parser = OptionParser()
parser.add_option('-s', '--sender', dest='sender',
                  help='file for sender of the mail', default=None)
parser.add_option('-r', '--receiver', dest='receiver', type='string',
                  help='list file for receivers of the mail', default=None)
parser.add_option('-t', '--title', dest='title', type='string',
                  help='title of the email,string',
                  default='Not reply, this is auto email.')
parser.add_option('-a', '--attach', dest='attach', type='string',
                  help='attachment of the file', default=None)
parser.add_option('-c', '--content', dest='content',
                  help='information of the content.', default=None)
(options, args) = parser.parse_args()

msgRoot = MIMEMultipart()


# get the username and pasword
def getsender(args):
    if args is None:
        print '未指定发件人信息，将使用默认发件人；默认发件人信息保存在data/sender.lst文件中。'
        args = './data/sender.lst'
        upf = open(args)
        username = upf.readline()
        password = upf.readline()
        upf.close()
        senderinfo = (username.strip(os.linesep), password.strip(os.linesep))
        return senderinfo
    elif os.path.isfile(args):
        upf = open(args)
        username = upf.readline()
        password = upf.readline()
        upf.close()
        senderinfo = (username.strip(os.linesep), password.strip(os.linesep))
        return senderinfo
    else:
        print '请指定保存发件人信息的文件路径，或将发件人信息保存在默认的data/sender.lst文件中。'
        exit(0)


# get the receiver list
def getReceiverLst(args):
    if args is None:
        print '未指定正确的收件人信息，默认收件人信息保存在data/receiver.lst文件中。'
        exit(0)
    elif os.path.isfile(args):
        lif = open(args)
        li = lif.readlines()
        lif.close()
        for x in range(len(li)):
            li[x] = li[x].strip().strip(os.linesep)
        while '' in li:
            li.remove('')
        return (li)
    else:
        print '请指定正确的接收列表路径。'
        exit(0)


# get mail text of the mail
def getText(args):
    file_name = args
    # 如果未指定邮件正文的文件路径，则默认正文为空
    if args is None:
        pass
    # 如果指定邮件正文的文件路径存在，则将附件添加到要容器
    elif os.path.exists(file_name):
        data = open(file_name, 'rb')
        s = data.read()
        data.close()
        # 构造MIMEText对象做为邮件显示内容并附加到根容器
        text_msg = email.MIMEText.MIMEText(s, _charset="utf-8")
        msgRoot.attach(text_msg)
    # 如果指定邮件正文的文件路径不存在，则默认用户想添加正文但写错路径，程序退出。
    else:
        print '请指定正确的附件路径。'
        exit(0)


# get attach
def getAttachment(filename):
    print 'You have attach file path is {}'.format(filename)
    # 如果未指定附件路径，则默认不添加附件。
    if filename is None:
        pass
    # 如果指定路径附件存在，则将附件添加到要容器
    elif os.path.exists(filename):
        # 构造MIMEBase对象做为文件附件并附加到根容器
        contype = 'application/octet-stream'
        maintype, subtype = contype.split('/', 1)
        attfile = MIMEBase(maintype, subtype)

        # 设置附件头
        basename = os.path.basename(filename)
        attfile.add_header('Content-Disposition', 'attachment',
                           filename=basename)
        msgRoot.attach(attfile)
    # 如果指定路径附件不存在，则默认用户想添加附件但写错路径，程序退出。
    else:
        print '请指定正确的附件路径。'
        exit(0)


def getSmtpServer(args):
    '''
    传入一个邮箱地址，自动根据@后面的内容判断smtp服务器
    可以更新serverlib库
    '''
    serverlib = {
                 '163.com': 'smtp.163.com',
                 'qq.com': 'smtp.qq.com',
                 '126.com': 'smtp.126.com',
                 'gmail.com': 'smtp.gmail.com'
                }
    print '自动检测Smtp Server ……'
    x = args.split('@')[1]
    if x in serverlib:
        smtp_server = serverlib[x]
        return smtp_server


def main():
    senderlst = getsender(options.sender)
    receiverlst = getReceiverLst(options.receiver)

    # title,sender,receiver
    msgRoot['Subject'] = options.title
    msgRoot['From'] = senderlst[0]
    msgRoot['To'] = ';'.join(receiverlst)
    # add mail text
    getText(options.content)
    # add attachment
    getAttachment(options.attach)

    mailsmtp = smtplib.SMTP()
    theServer = getSmtpServer(senderlst[0])
    username = senderlst[0]
    password = senderlst[1]
    try:
        print (time.strftime('%Y-%m-%d %X', time.localtime(time.time())))
        mailsmtp.connect(theServer)
        mailsmtp.login(username, password)
    except Exception, e:
        print "Error when connect the smtpserver !"
        print e
        exit(0)

    print "connected smtp server!"

    try:
        # 得到格式化后的完整文本
        fulltext = msgRoot.as_string()
        print fulltext
        # 用smtp发送邮件
        mailsmtp.sendmail(senderlst[0], receiverlst, fulltext)
    except Exception, e:
        print e
    finally:
        mailsmtp.quit()

    print 'Email to ' + str(receiverlst) + ' over.'


if __name__ == '__main__':
    main()
