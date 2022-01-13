# _*_ coding:utf-8 _*_
# _*_ author:yangchenguang _*_
from flask import request, jsonify
from flask import Blueprint
from generate_token import certify_token
import time
import json
from db_connection import MysqlClient
from common import check, page_size, check_login_status, gen_sql
iteration = Blueprint('iteration_manage', __name__)
db = MysqlClient()


@iteration.route('/iteration_manage/group/create', methods=["POST"])
@check_login_status
def new_iteration_group():
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        a = request.get_json()
        user_id = int(token_result)
        iteration_group_name = str(a['iteration_group_name'])
        group_push_address = a['group_push_address']
        if iteration_group_name == '' or group_push_address == '':
            return jsonify({"code": 2222, "message": "必传字段不能为空"})
        user_check_sql = 'select id from users where id = %d limit 1' % user_id
        res = db.select_one(user_check_sql)
        if res is None:
            return jsonify({"code": 2222, "message": "用户不存在"})
        check_group_name_sql = "select iteration_group_name from iteration_groups where iteration_group_name = '%s'" \
                               % iteration_group_name
        res_name = db.select_one(check_group_name_sql)
        print(res_name)
        if res_name:
            return jsonify({"code": 2222, "message": "名称重复,请更换", "result": None})
        else:
            try:
                insert_sql = "insert into iteration_groups (user_id,iteration_group_name,group_push_address) " \
                             "values(%d,'%s','%s')" % (user_id, iteration_group_name, group_push_address)
                db.add_one(insert_sql)
                return jsonify({"code": 200, "message": "success", "result": None})
            except:
                db.end()
                return jsonify({"code": 2222, "message": "系统异常"})

    else:
        return jsonify({"code": 2222, "message": "token信息错误", "result": None})


@iteration.route('/iteration_manage/group/updateStatus', methods=["PUT"])
@check_login_status
def update_iteration_group_status():
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        a = request.get_json()
        user_id = token_result
        iteration_group_id = a['id']
        if iteration_group_id is None:
            return jsonify({"code": 2222, "message": "id不能为空"})
        user_check_sql = 'select id from users where id = %d limit 1' % user_id
        res = db.select_one(user_check_sql)
        if res is None:
            return jsonify({"code": 2222, "message": "用户不存在"})

        # 检查该小组是否有已使用的迭代版本
        check_used_sql = "select count(1) as num from iterations where iteration_group_id = %d and is_delete=0" \
                         % iteration_group_id
        used_num = db.select_one(check_used_sql)
        if used_num['num'] > 0:
            return jsonify({"code": 2222, "message": "该小组已被迭代版本使用，暂不能删除", "result": None})
        # 检查iteration_group_id是否有效
        check_group_name_sql = "select id from iteration_groups where id = %d and is_delete=0" % iteration_group_id
        res_id = db.select_one(check_group_name_sql)
        if res_id:
            operation_time = time.strftime("%Y-%m-%d %H:%m:%S", time.localtime())
            update_sql = "update iteration_groups set is_delete =1 ,user_id = %d,update_time='%s' where id= %d " \
                % (user_id, operation_time, iteration_group_id,)
            db.edit_one(update_sql)
            return jsonify({"code": 200, "message": "success", "result": None})
        else:
            return jsonify({"code": 2222, "message": "id错误", "result": None})
    else:
        return jsonify({"code": 2222, "message": "token信息错误", "result": None})


@iteration.route('/iteration_manage/group/edit', methods=["POST"])
@check_login_status
def edit_iteration_group_info():
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        a = request.get_json()
        user_id = token_result
        iteration_group_name = a['iteration_group_name']
        iteration_group_id = a['id']
        group_push_address = a['group_push_address']
        if iteration_group_name == '' or group_push_address == '':
            return jsonify({"code": 2222, "message": "必传字段不能为空"})
        elif iteration_group_name is None or iteration_group_id is None :
            return jsonify({"code": 2222, "message": "缺少必传字段"})

        check_group_name_sql = "select id from iteration_groups where iteration_group_name='%s'and is_delete=0 limit 1" \
                               % iteration_group_name
        compare_id = db.select_one(check_group_name_sql)
        if compare_id['id'] == iteration_group_id:
            try:
                update_sql = "update iteration_groups set iteration_group_name ='%s', group_push_address='%s'," \
                             "user_id = %d where id= %d " \
                             % (iteration_group_name, group_push_address, user_id, iteration_group_id)
                print(update_sql)
                db.edit_one(update_sql)
                return jsonify({"code": 200, "message": "success", "result": None})
            except:
                db.end()
            return jsonify({"code": 2222, "message": "系统异常"})
        else:
            return jsonify({"code": 2222, "message": "名称重复请更换", "result": None})
    else:
        return jsonify({"code": 2222, "message": "token信息错误", "result": None})


# 全部——条件 查询
@iteration.route('/iteration_manage/group/list', methods=["GET"])
@check_login_status
def get_iteration_group_list():
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        group_name = str(request.args.get("iteration_group_name"))
        start_at = str(request.args.get("start_time"))
        end_at = str(request.args.get("update_time"))
        if group_name == '' and start_at == '' and end_at == '':
            total_count_sql = "select count(1) as num from iteration_groups where is_delete = 0 "
            res_num = db.select_one(total_count_sql)
            if res_num['num'] > 0:
                detail_info_sql = "select ig.*,u.user_name from iteration_groups ig " \
                                  "left join users u on ig.user_id=u.id " \
                                  "where ig.is_delete = 0 order by ig.id desc "
                detail_info = db.select_many(detail_info_sql)
                return jsonify({"code": 200, "message": "success", "result": detail_info, "totalCount": res_num["num"]})
            else:
                return jsonify({"code": 200, "message": "success", "result": []})
        # 查询条件都不为空
        if (group_name and start_at and end_at) != '':
            total_count_sql = "select count(1)as num from iteration_groups ig left join users u on ig.user_id=u.id " \
                              "where ig.is_delete = 0 and ig.create_time between '%s' and '%s' " \
                              "and iteration_group_name like '%%%s%%' " % (start_at, end_at, group_name)
            res_num = db.select_one(total_count_sql)
            if res_num['num'] > 0:
                name_info_sql = "select ig.*,u.user_name from iteration_groups ig left join users u on ig.user_id=u.id " \
                              "where ig.is_delete = 0 and ig.create_time between '%s' and '%s' " \
                              "and iteration_group_name like '%%%s%%' " % (start_at, end_at, group_name)
                name_info = db.select_many(name_info_sql)
                return jsonify({"code": 200, "message": "success", "result": name_info, "totalCount": res_num["num"]})
            else:
                return jsonify({"code": 200, "message": "success", "result": []})
        elif group_name != '':
            total_count_sql = "select count(1)as num from iteration_groups ig left join users u on ig.user_id=u.id " \
                              "where ig.is_delete = 0 and ig.iteration_group_name like '%%%s%%' " \
                              % group_name
            res_num = db.select_one(total_count_sql)
            if res_num['num'] > 0:
                name_info_sql = "select ig.*,u.user_name from iteration_groups ig " \
                                "left join users u on ig.user_id=u.id " \
                              "where ig.is_delete = 0 and ig.iteration_group_name like '%%%s%%' order by ig.id desc  " \
                              % group_name
                name_info = db.select_many(name_info_sql)
                return jsonify({"code": 200, "message": "success", "result": name_info, "totalCount": res_num["num"]})
            else:
                return jsonify({"code": 200, "message": "success", "result": []})
        elif start_at != '' and end_at != '':
            total_count_sql = "select count(1)as num from iteration_groups ig left join users u on ig.user_id=u.id " \
                            "where ig.is_delete = 0 and ig.create_time between '%s' and '%s' " % (start_at, end_at)
            res_num = db.select_one(total_count_sql)
            if res_num['num'] > 0:
                time_info_sql = "select ig.*,u.user_name from iteration_groups ig " \
                                "left join users u on ig.user_id=u.id " \
                                "where ig.is_delete = 0 and ig.create_time between '%s' and '%s' " \
                                "order by ig.create_time desc " \
                                % (start_at, end_at)
                time_info = db.select_many(time_info_sql)
                return jsonify({"code": 200, "message": "success", "result": time_info})
            else:
                return jsonify({"code": 200, "message": "success", "result": []})
        else:
            return jsonify({"code": 2222, "message": "系统异常", "result": None})

    else:
        return jsonify({"code": 2222, "message": "token信息错误", "result": None})


# user模块查询groups
@iteration.route('/user/groupList', methods=["GET"])
@check_login_status
def user_group_list():
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        group_sql = "select id,iteration_group_name from iteration_groups where is_delete = 0 order by id desc"
        group_info = db.select_many(group_sql)
        return jsonify({"code": 200, "message": "success", "result": group_info})
    else:
        return jsonify({"code": 2222, "message": "无效token"})

