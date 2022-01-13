# _*_ coding:utf-8 _*_
# _*_ author:yangchenguang _*_
from flask import request, jsonify
from flask import Blueprint
from generate_token import certify_token
import time
import json
from db_connection import MysqlClient
from common import check, page_size, check_login_status, gen_sql, gen_sql_count
iteration_version = Blueprint('iteration_version', __name__)
db = MysqlClient()


@iteration_version.route('/iteration_manage/version/create', methods=["POST"])
def new_iteration_version():
    required_params = ['iteration_group_id', 'iteration_version']
    a = request.get_json()
    res = check(a, required_params)
    if res is not None:
        msg = "%s是必传字段" % res
        return jsonify({"code": 2222, "message": msg})
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        a = request.get_json()
        user_id = int(token_result)
        iteration_group_id = int(a['iteration_group_id'])
        iteration_version_name = a['iteration_version']
        if iteration_version_name == '' or iteration_group_id !=0:
            return jsonify({"code": 2222, "message": "必传字段不能为空"})

        # 用户id校验
        user_check_sql = 'select id from users where id = %d limit 1' % user_id
        res = db.select_one(user_check_sql)
        if res is None:
            return jsonify({"code": 2222, "message": "用户不存在"})
        # 迭代小组id校验
        if iteration_group_id < 0:
            return jsonify({"code": 2222, "message": "无效的迭代小组id"})
        else:
            sql_group_check = "select * from iteration_groups where id = %d and is_delete = 0" % iteration_group_id
            group_res = db.select_one(sql_group_check)
            if group_res is None:
                return jsonify({"code": 2222, "message": "迭代小组id错误"})
            else:
                try:
                    insert_sql = "insert into iterations (user_id,iteration_group_id,iteration_version) " \
                                 "values(%d,%d,'%s')" \
                                 % (user_id, iteration_group_id, iteration_version_name)
                    db.add_one(insert_sql)
                    return jsonify({"code": 200, "message": "success", "result": None})
                except:
                    db.end()
                    return jsonify({"code": 2222, "message": "系统异常","result": None})
    else:
        return jsonify({"code": 2222, "message": "token信息错误", "result": None})


@iteration_version.route('/iteration_manage/version/update', methods=["PUT"])
def update_iteration():
    a = request.get_json()
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        user_id = int(token_result)
        iteration_id = a['id']
        if iteration_id is None:
            return jsonify({"code": 2222, "message": "id不能为空"})
        # user_check_sql = 'select id from users where id = %d limit 1' % user_id
        # res = db.select_one(user_check_sql)
        # if res is None:
        #     return jsonify({"code": 2222, "message": "用户不存在"})

        # 检查该版本是否有已使用的提测记录
        check_used_sql = "select count(1) as num from iteration_submit_records where iteration_version_id = %d " \
                         "and is_delete=0" % iteration_id
        used_num = db.select_one(check_used_sql)
        if used_num['num'] > 0:
            return jsonify({"code": 2222, "message": "该迭代版本已使用，不能删除", "result": None})

        check_id_sql = "select id from iterations where id = %d" % iteration_id
        res_id = db.select_one(check_id_sql)
        print(res_id)
        if res_id:
            try:
                update_sql = "update iterations set is_delete =1 and user_id = %d where id= %d " \
                    % (user_id, iteration_id)
                db.edit_one(update_sql)
                return jsonify({"code": 200, "message": "success", "result": None})
            except:
                db.end()
        else:
            return jsonify({"code": 2222, "message": "无效id", "result": None})
    else:
        return jsonify({"code": 2222, "message": "token信息错误", "result": None})


@iteration_version.route('/iteration_manage/version/edit', methods=["put"])
def edit_iteration_info():
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        a = request.get_json()
        user_id = token_result
        new_iteration_group_id = a['iteration_group_id']
        iteration_version_name = a['iteration_version']
        iteration_id = a['id']
        if iteration_version is None or new_iteration_group_id is None:
            return jsonify({"code": 2222, "message": "必填字段不能为空"})
        check_id_sql = "select id,iteration_group_id from iterations where id = %d" % iteration_id
        res_iteration_info = db.select_one(check_id_sql)
        old_iteration_group_id = res_iteration_info["iteration_group_id"]
        check_group_id_sql = "select id from iteration_groups where id = %d and is_delete=0" % new_iteration_group_id
        res_group_id = db.select_one(check_group_id_sql)
        if res_iteration_info is None or res_group_id is None:
            return jsonify({"code": 2222, "message": "无效的id或无效的iteration_group_id", "result": None})

        elif old_iteration_group_id == new_iteration_group_id:
            try:
                update_sql = "update iterations set iteration_version ='%s', user_id = %d  where id= %d " \
                             % (iteration_version_name, user_id, iteration_id)
                print(update_sql)
                db.edit_one(update_sql)
                return jsonify({"code": 200, "message": "success", "result": None})
            except:
                db.end()
                return jsonify({"code": 2222, "message": "系统异常", "result": None})
        else:
            try:
                update_sql = "update iterations set iteration_version ='%s', user_id = %d ," \
                             "iteration_group_id=%d where id= %d " \
                             % (iteration_version_name, user_id, new_iteration_group_id, iteration_id)
                print(update_sql)
                db.edit_one(update_sql)
                return jsonify({"code": 200, "message": "success", "result": None})
            except:
                db.end()
                return jsonify({"code": 2222, "message": "系统异常", "result": None})
    else:
        return jsonify({"code": 2222, "message": "无效的token", "result": None})


@iteration_version.route('/iteration_manage/version/list', methods=["get"])
def get_iteration_group_list():
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        data_page_size = int(request.args.get("page_size"))
        start = int(request.args.get("page_index"))
        iteration_group_id = str(request.args.get("iteration_group_id"))
        version = request.args.get("iteration_version")
        request_data = {
            "i.iteration_group_id": iteration_group_id,
            "i.iteration_version": version
        }
        total_count_sql = "select count(1) as num from iterations where is_delete = 0 "
        res_num = db.select_one(total_count_sql)
        total_num = res_num["num"]
        if total_num > 0:
            # limit_start_num = int(start - 1) * data_page_size
            sql_end = " order by i.id desc "
            sql_start = "select i.*,u.user_name,ig.iteration_group_name " \
                        "from iterations i left join iteration_groups ig on i.iteration_group_id = ig.id "\
                        "left join users u on i.user_id = u.id  where i.is_delete=0 "

            sql_find_count = "select count(1) as num  " \
                             "from iterations i left join iteration_groups ig on i.iteration_group_id = ig.id "\
                             "left join users u on i.user_id = u.id  where i.is_delete=0 "
            user_count_sql_2 = gen_sql_count(sql_find_count, request_data)
            fin_res_num = db.select_one(user_count_sql_2)
            find_count = fin_res_num['num']
            version_all_info_sql = gen_sql(sql_start, request_data, sql_end, start, data_page_size)
            all_version = db.select_many(version_all_info_sql)
            page_cnt = page_size(total_num, data_page_size)
            if start <= page_cnt:
                return jsonify(
                    {"code": 200,
                     "message": "success",
                     "result": all_version,
                     "currentPage": start, "pageSize": data_page_size,
                     "totalPage": page_cnt, "total": find_count,
                     })
            else:
                return jsonify({"code": 200, "message": "success", "result": [], "total": 0})
        else:
            return jsonify({"code": 200, "message": "success", "result": [], "total": 0})
    else:
        return jsonify({"code": 2222, "message": "token信息错误", "result": None})


@iteration_version.route('/iteration_manage/version/VersionListByUser', methods=["get"])
def find_iteration_version_list_by_user_id():
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        user_id = token_result
        user_version_sql = "select i.id,i.iteration_version from users u left join iterations i " \
                           "on u.iteration_group_id = i.iteration_group_id where i.is_delete=0 " \
                           "and u.id = %d order by i.id desc limit 5 " % user_id

        user_all_version = db.select_many(user_version_sql)

        return jsonify({"code": 200, "message": "success", "result": user_all_version})

    else:
        return jsonify({"code": 2222, "message": "token信息错误", "result": None})
