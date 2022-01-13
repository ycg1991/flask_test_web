# _*_ coding:utf-8 _*_
from flask import request, jsonify, redirect
from functools import wraps
import requests
import json
# from WorkWeixinRobot.work_weixin_robot import WWXRobot


# 必传字段校验
def field_check(request_form, required):
    if not all(k in request_form for k in required):
        return 'false'
    else:
        return 'true'


# 必传字段校验
def check(request_form, required):
    r_list = []
    # for i in required:
    #     if len(str(request_form[i])) > 0:
    #         cnt = cnt + 1
    for key, value in request_form.items():
        r_list.append(key)
    for i in required:
        if i not in r_list:
            return i


# 数据页数
def page_size(all_cnt, appear_page):
    page_cnt, c = divmod(all_cnt, appear_page)
    if c > 0:
        page_cnt = page_cnt + 1
    return page_cnt


# token 验证
# def check_token():
#     header_info = request.headers
#     print(header_info)
#     if "Token" not in header_info.keys():
#         return jsonify({"code": 2222, "message": "缺少token", "result": None})
#     token = certify_token(header_info["token"])


def check_login_status(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        header_info = request.headers
        if header_info["Authorization"]:
            return func(*args, **kwargs)
        else:
            # 否则重定向到登录页面
            return redirect("/user/login")
    return wrapper


# 拼装查询语句的sql,过滤掉空值条件
def gen_sql(sql_start, s, sql_end, limit_start_num, data_page_size):
    last = []
    values = list()
    str_3 = ""
    start_index = int((limit_start_num-1) * data_page_size)
    print(start_index)
    sql_limit = "limit " + str(start_index) + "," + str(data_page_size)
    for a in s.keys():
        if s[a] == '':
            last.append(a)
    for i in last:
        s.pop(i)
    for k, v in s.items():
        values.append(v)
        str_2 = " and " + k + "=" + "'{}'"
        str_3 += str_2
    sql = (sql_start + str_3).format(*values) + sql_end + sql_limit
    return sql


# 生成查询总数的sql
def gen_sql_count(sql_start, s):
    last = []
    values = list()
    str_3 = ""
    for a in s.keys():
        if s[a] == '':
            last.append(a)
    for i in last:
        s.pop(i)
    for k, v in s.items():
        values.append(v)
        str_2 = " and " + k + "=" + "'{}'"
        str_3 += str_2
    sql = (sql_start + str_3).format(*values)
    return sql


# 向企业微信发送消息
def send_ready_message(address, group_name, version, story_id, content,
                       story_type, unittest, develop_person, user_name, sql, effect, mark):
    header = {
        "Content-Type": "application/json"
    }
    body_data = {

        "msgtype": "markdown",
        "markdown": {
            "content": "# **您有一份新的提测单，请查看！**\n"
                        "> 迭代组：<font color=\"info\">%s</font> \n"
                        "> 迭代版本：<font color=\"info\">%s</font> \n"
                        "> story_id：<font color=\"info\">%s</font>\n"
                        "> 需求内容：<font color=\"info\">%s</font>\n"
                        "> 需求处理端：<font color=\"info\">%s</font>\n"
                        "> 单元测试：<font color=\"info\">%s</font>\n"
                        "> 参与研发：<font color=\"info\">%s</font>\n"
                        "> 提交人：<font color=\"info\">%s</font>\n"
                        "> sql工单：<font color=\"info\">%s</font>\n"
                        "> 影响范围：<font color=\"info\">%s</font>\n"
                        "> 备注：<font color=\"info\">%s</font>\n"
                        % (group_name, version, story_id, content, story_type,
                           unittest, develop_person, user_name, sql, effect, mark),
            "mentioned_mobile_list": ["@all"]
        }
    }
    r = requests.post(url=address, data=json.dumps(body_data), headers=header)
    return r.status_code


# 冒烟结果发送消息
def smoke_result_message(address, group_name, version, story_id, content, story_type,
                         smoke_result, smoke_user_name, smoke_mark, develop_person):
    header = {
        "Content-Type": "application/json"
    }
    body_data = {
        "msgtype": "markdown",
        "markdown": {
         "content": "# **冒烟结果通知！**\n"
                    "> 迭代组：<font color=\"info\">%s</font> \n"
                    "> 迭代版本：<font color=\"info\">%s</font> \n"
                    "> story_id：<font color=\"info\">%s</font>\n"
                    "> 需求内容：<font color=\"info\">%s</font>\n"
                    "> 需求处理端：<font color=\"info\">%s</font>\n"
                    "> 冒烟结果：<font color=\"info\">%s</font>\n"
                    "> 备注：<font color=\"info\">%s</font>\n"
                    "> 冒烟用户：<font color=\"info\">%s</font>\n"
                    "> 参与研发：<font color=\"info\">%s</font>\n"
                    % (group_name, version, story_id, content, story_type, smoke_result,
                       smoke_user_name, smoke_mark, develop_person)

        }
    }
    r = requests.post(url=address, data=json.dumps(body_data), headers=header)
    return r.status_code
