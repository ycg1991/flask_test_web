# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header
import config


def uat_pass_mail(a):
    # 构造邮件模板内容
    msg_body = '<body><div><table border="1" cellspacing="0" cellpadding="0" width="80%">' \
                '<tr class="table_common"><th class="table_title" colspan="4" >' \
                '' + a['release_version'] + 'UAT验收报告' + '</th></tr>'\
                '<tr class="table_common"><td>UAT参与人</td><td>' + '' + a['name'] + '</td><td>UAT时间</td>'\
                '<td>' + '' + a['date'] + '</td></tr>' \
                '<tr class ="table_common"><td colspan="2">需求地址</td> '\
                '<td colspan="2"> ' + '' + a['prd_url'] + ' </td></tr>' \
                '<tr class ="table_common"><td colspan="2" >需求OP地址</td>' \
                '<td colspan="2"> ' + '' + a['op_url'] + '</td></tr>'\
                '<tr class="table_common"><td colspan="2">uat验收情况</td>'\
                '<td colspan="2">' + '' + a['uat_result'] + '</td></tr>'\
                '<tr class="table_high"><td colspan="2">uat用例</td>'\
                '<td colspan="2">' + '' + a['uat_case'] + '</td></tr>'\
                '<tr class="table_high"><td colspan="2">遗留问题</td>'\
                '<td colspan="2">' + '' + a['other_question'] + '</td></tr>'\
                '<style type="text/css">table{text-align: center;}.table_common{height: 70px;}' \
                '.table_title{background: yellow;}.table_high{height: 200px;}'
    msg_head = '<html lang="en"><head><meta charset="UTF-8"></head>'
    msg_end = '</table><div></body></html>'
    mail_msg = msg_head + msg_body + msg_end
    message = MIMEText(mail_msg, 'html', 'utf-8')
    # 邮件标题
    message['From'] = Header("UAT验收报告", 'utf-8')
    message['To'] = Header("测试", 'utf-8')
    subject = 'UAT验收报告'
    message['Subject'] = Header(subject, 'utf-8')
    server = None
    # 发送邮件
    try:
        server = smtplib.SMTP_SSL(config.mail_host, 465)
        server.login(config.mail_user, config.mail_pwd)
        server.sendmail(config.sender, config.listener, message.as_string())
        print("成功")
    except smtplib.SMTPException:
        print("失败")
    finally:
        server.quit()

