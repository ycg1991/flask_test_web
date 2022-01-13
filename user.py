# _*_ coding:utf-8 _*_
# _*_ author:yangchenguang _*_

from flask import request, session, g, jsonify
import time
from generate_token import generate_token, certify_token
from flask import Blueprint
from db_connection import MysqlClient
from common import check, page_size, check_login_status, gen_sql, gen_sql_count
user = Blueprint('user', __name__)
db = MysqlClient()


# 登录
@user.route('/user/login', methods=["POST"])
def user_login():
    a = request.get_json()
    user_mobile = str(a['user_mobile'])
    user_password = str(a['user_password'])
    required_params = ['user_mobile', 'user_password']
    res = check(a, required_params)
    if res is not None:
        msg = "%s是必传字段" % res
        return jsonify({"code": 2222, "message": msg})
    sql_2 = "select is_delete from users where user_mobile='%s'" % user_mobile
    result = db.select_one(sql_2)
    if result:
        user_status = result["is_delete"]
        if user_status == 1:
            return jsonify({"code": 2222, "message": "账号已停用"})
        elif user_status == 0:
            sql_1 = "select * from users where user_mobile='%s' and user_password='%s' and is_delete=0 " \
                    % (user_mobile, user_password)
            result_info = db.select_one(sql_1)
            if result_info:
                user_id = result_info["id"]
                user_name = result_info["user_name"]
                user_role = result_info["user_role"]
                user_token = generate_token(user_id)
                return jsonify({
                                "code": 200, "message": "success",
                                "result": {"token": user_token, "id": user_id, "user_name": user_name,
                                           "user_role": user_role}
                                })
            else:
                return jsonify({"code": 2222, "message": "用户名或密码错误"})

    else:
        return jsonify({"code": 2222, "message": "账号不存在"})


# 新增用户
@user.route('/user/add', methods=["POST"])
def add_user_account():
    required_params = ['user_name', 'user_mobile', 'user_role', 'user_password', 'iteration_group_id', 'user_email']
    a = request.get_json()
    res = check(a, required_params)
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        if res is None:
            user_name = str(a['user_name'])
            user_password = str(a['user_password'])
            user_mobile = str(a['user_mobile'])
            iteration_group_id = a['iteration_group_id']
            user_role = int(a['user_role'])
            user_email = a['user_email']
            if len(user_mobile) == 0 or len(user_name) == 0 or len(user_password) == 0 or len(str(user_role)) == 0:
                return jsonify({"code": 2222, "message": "必填字段不能为空", "result": None})
            group_check_sql = "select count(1) as num from iteration_groups where id =%d and is_delete=0 " % iteration_group_id
            group_info = db.select_one(group_check_sql)
            if group_info["num"] != 1:
                return jsonify({"code": 2222, "message": "迭代小组信息错误", "result": None})
            if user_role > 6 or user_role <= 0:
                return jsonify({"code": 2222, "message": "用户角色信息错误", "result": None})
            mobile_check_sql = "select * from users where user_mobile='%s' and is_delete=0 " % user_mobile
            result = db.select_one(mobile_check_sql)
            if result:
                return jsonify({"code": 2222, "message": "手机号已存在"})
            else:
                try:
                    sql_2 = "insert into users " \
                            "(user_name,user_mobile,user_email,user_password,user_role,iteration_group_id)" \
                            " values ('%s','%s','%s','%s',%d, %d)" \
                            % (user_name, user_mobile, user_email, user_password, user_role, iteration_group_id)
                    print(sql_2)
                    db.add_one(sql_2)
                    return jsonify({"code": 200, "message": "success", "result": None})
                except:
                    db.end()
                    return jsonify({"code": 2222, "message": "系统异常", "result": None})
        else:
            msg = "%s是必传字段" % res
            return jsonify({"code": 2222, "message": msg})
    else:
        return jsonify({"code": 2222, "message": "token信息错误"})


# 用户查询
@check_login_status
@user.route('/user/list', methods=["get"])
def user_list_all():
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        iteration_group_id = str(request.args.get("iteration_group_id"))
        user_mobile = str(request.args.get("user_mobile"))
        user_role = str(request.args.get("user_role"))
        user_name = str(request.args.get("user_name"))
        start = request.args.get("page_index")
        data_page_size = request.args.get("page_size")
        request_data = {
            "iteration_group_id": iteration_group_id,
            "user_mobile": user_mobile,
            "user_role": user_role,
            "user_name": user_name
        }
        sql_count = "select count(1) as num from users u left join iteration_groups ig on u.iteration_group_id=ig.id " \
                    "where u.is_delete=0 "
        user_count_sql = gen_sql_count(sql_count, request_data)
        res_num = db.select_one(user_count_sql)
        all_count = res_num['num']
        if all_count > 0:
            # limit_start_num = int(start - 1) * data_page_size
            if start is None and data_page_size is None:
                start = 1
                data_page_size = 10
            else:
                start = int(start)
                data_page_size = int(data_page_size)
            sql_end = "order by u.id desc "
            sql_start = "select u.id,u.user_name,u.user_mobile,u.user_role,u.user_email," \
                        "u.create_time,u.update_time,u.iteration_group_id,ig.iteration_group_name from " \
                        "users u left join iteration_groups ig on u.iteration_group_id=ig.id where " \
                        "u.is_delete=0 "
            sql_find_count = "select count(1) as num from " \
                             "users u left join iteration_groups ig on u.iteration_group_id=ig.id where " \
                             "u.is_delete=0 "
            user_count_sql_2 = gen_sql_count(sql_find_count, request_data)
            fin_res_num = db.select_one(user_count_sql_2)
            find_count = fin_res_num['num']
            user_all_info_sql = gen_sql(sql_start, request_data, sql_end, start, data_page_size)
            all_user = db.select_many(user_all_info_sql)
            page_cnt = page_size(find_count, data_page_size)
            if start <= page_cnt:
                return jsonify(
                    {"code": 200,
                     "message": "success",
                     "result": all_user,
                     "currentPage": start, "pageSize": data_page_size,
                     "totalPage": page_cnt, "total": all_count,
                     })
            else:
                return jsonify({"code": 200, "message": "success", "result": [], "total": 0})
        else:
            return jsonify({"code": 200, "message": "success", "result": [], "total": 0})
    else:
        return jsonify({"code": 2222, "message": "无效的token", "result": None})


# 删除用户
@user.route('/user/list/delete', methods=["put"])
def delete_user():
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        a = request.get_json()
        user_id = int(a['id'])
        operate_user_id = int(token_result)
        if user_id == operate_user_id:
            return jsonify({"code": 2222, "message": "不能删除自己的账号", "result": None})
        else:
            try:
                sql_2 = "update users set is_delete =1 where id=%d" % user_id
                print(sql_2)
                db.edit_one(sql_2)
                return jsonify({"code": 200, "message": "success", "result": None})
            except:
                db.end()
                return jsonify({"code": 2222, "message": "系统异常", "result": None})
    else:
        return jsonify({"code": 2222, "message": "无效的token"})


# 改登录密码
@user.route('/user/updatePassword', methods=["put"])
def update_user_password():
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        user_id = int(token_result)
        user_password = request.args.get('user_password')
        if user_password == '':
            return jsonify({"code": 2222, "message": "密码不能为空", "result": None})
        else:
            try:
                sql_2 = "update users set user_password ='%s' where id='%s' " % (user_password, user_id)
                print(sql_2)
                db.edit_one(sql_2)
                return jsonify({"code": 200, "message": "success", "result": None})
            except:
                db.end()
                return jsonify({"code": 2222, "message": "系统繁忙"})
    else:
        return jsonify({"code": 2222, "message": "无效的token", "user": "false"})


@user.route('/user/list/edit', methods=["put"])
def update_user_info():
    required_params = ['user_name', 'user_mobile', 'user_role', 'iteration_group_id', 'user_email', 'id']
    a = request.get_json()
    res = check(a, required_params)
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        if res is None:
            a = request.get_json()
            users_id = int(a['id'])
            operate_user_id = int(token_result)
            user_name = str(a['user_name'])
            user_mobile = str(a['user_mobile'])
            iteration_group_id = a['iteration_group_id']
            user_role = int(a['user_role'])
            user_email = a['user_email']
            sql_1 = "select id from users where id =%d" % users_id
            result = db.select_one(sql_1)

            if result:
                user_mobile_check = "select id from users where is_delete = 0 and user_mobile='%s'" % user_mobile
                res = db.select_one(user_mobile_check)
                if users_id != operate_user_id:
                    return jsonify({"code": 2222, "message": "不能操作他人账号", "result": None})
                elif users_id != res["id"]:
                    return jsonify({"code": 2222, "message": "用户手机号不能重复", "result": None})
                else:
                    try:
                        sql_2 = "update users set user_name ='%s',user_mobile='%s', user_email='%s', " \
                                "iteration_group_id=%d, user_role=%d where id=%d" \
                                % (user_name, user_mobile, user_email, iteration_group_id, user_role, users_id)
                        db.edit_one(sql_2)
                        return jsonify({"code": 200, "message": "success", "result": None})
                    except:
                        db.end()
                        return jsonify({"code": 2222, "message": "用户信息编辑失败", "result": None})
            else:
                return jsonify({"code": 2222, "message": "系统异常", "result": None})
        else:
            msg = "%s是必传字段" % res
            return jsonify({"code": 2222, "message": msg})
    else:
        return jsonify({"code": 2222, "message": "token信息错误"})


@user.route('/logout', methods=["get"])
def logout():
    return jsonify({"code": 200, "message": "success", "result": None})


