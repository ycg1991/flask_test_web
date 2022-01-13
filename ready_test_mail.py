# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header
import config


def ready_test_mail(group_name, version, iteration_story_id, iteration_story_content, iteration_story_type,
                    unittest_status, develop_person, user_name, iteration_mysql, iteration_effect, mark):
    # 构造邮件模板内容
    msg_body = "<body><div><table class='mailTable'" \
                "style='width:100%;border-top: 1px solid #E6EAEE;border-left: 1px solid #E6EAEE;"\
                "cellspacing='0' cellpadding='0'>" \
                "<tr><td class='column'>迭代小组</td><td>" + "" + group_name + "</td></tr>"\
                "<tr><td class='column'>迭代版本</td><td>" + "" + version + "</td></tr>"\
                "<tr><td class='column'>需求id</td><td>" + "" + iteration_story_id+ "</td></tr>"\
                "<tr><td class='column'>需求内容</td><td>" + "" + iteration_story_content + "</td></tr>" \
                "<tr><td class='column'>提测端</td><td>" + "" + iteration_story_type + "</td></tr>" \
                "<tr><td class='column'>单元测试</td><td>" + "" + unittest_status + "</td></tr>" \
                "<tr><td class='column'>参与研发</td><td>" + "" + develop_person + "</td></tr>" \
                "<tr><td class='column'>工单执行</td><td>" + "" + iteration_mysql + "</td></tr>"\
                "<tr><td class='column'>提测人</td><td>" + "" + user_name+ "</td></tr>"\
                "<tr><td class='column'>影响范围</td><td>" + "" + iteration_effect + "</td></tr>"\
                "<tr><td class='column'>备注</td><td>" + "" + mark + "</td></tr>"\
                "<style type='text/css'>.mailTable tr td{width: 200px;height: 35px;line-height: 35px;box-sizing: " \
                "border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;}" \
                ".mailTable tr td.column{background-color:#EFF3F6;color:#393C3E;width:30%;}</style>"
    msg_head = '<html lang="en"><head><meta charset="UTF-8"></head>'
    msg_end = '</table><div></body></html>'
    mail_msg = msg_head + msg_body + msg_end
    message = MIMEText(mail_msg, 'html', 'utf-8')
    # 邮件标题
    message['From'] = Header("需求提测", 'utf-8')
    message['To'] = Header(group_name, 'utf-8')
    subject = '提测邮件'
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
        raise
    finally:
        server.quit()


ready_test_mail('1','2','3','4','5','6','7','8','9','10','11')
