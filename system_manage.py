# _*_ coding:utf-8 _*_
# _*_ author:yangchenguang _*_
from flask import request, jsonify
from flask import Blueprint
from generate_token import certify_token
import time
import json
from db_connection import MysqlClient
from common import check, page_size, check_login_status, gen_sql, gen_sql_count
system = Blueprint('system_manage', __name__)
db = MysqlClient()


@system.route('/system_manage/system/create', methods=["POST"])
def new_iteration_group():
    required_params = ['system_name', 'system_url', 'system_env', 'system_organization_id', 'system_organization_name']
    a = request.get_json()
    res = check(a, required_params)
    header_info = request.headers
    if res is not None:
        msg = "%s是必传字段" % res
        return jsonify({"code": 2222, "message": msg})
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        a = request.get_json()
        user_id = int(token_result)
        system_name = a['system_name']
        system_url = a['system_url']
        system_env = a['system_env']
        system_organization_id = a['system_organization_id']
        system_organization_name = a['system_organization_name']
        try:
            insert_sql = "insert into system_url_manage (user_id,system_name,system_url,system_env," \
                         "system_organization_id,system_organization_name) values(%d,'%s','%s','%s','%s','%s')" \
                         % (user_id, system_name, system_url,system_env,system_organization_id,system_organization_name)
            db.add_one(insert_sql)
            return jsonify({"code": 200, "message": "success", "result": None})
        except:
            db.end()
            return jsonify({"code": 2222, "message": "系统异常"})

    else:
        return jsonify({"code": 2222, "message": "token信息错误", "result": None})


@system.route('/system_manage/system/updateStatus', methods=["PUT"])
def update_iteration_group_status():
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        a = request.get_json()
        user_id = token_result
        system_id = a['id']
        if system_id is None:
            return jsonify({"code": 2222, "message": "id不能为空"})
        # 检查id是否有效
        check_id_sql = "select id,user_id from system_url_manage where id = %d and is_delete=0" % system_id
        res = db.select_one(check_id_sql)
        if res:
            if user_id != res['user_id']:
                return jsonify({"code": 2222, "message": "非本人创建的不能删除", "result": None})
            else:
                update_sql = "update system_url_manage set is_delete =1 ,user_id = %d where id= %d " \
                    % (user_id, system_id,)
                db.edit_one(update_sql)
            return jsonify({"code": 200, "message": "success", "result": None})
        else:
            return jsonify({"code": 2222, "message": "无效的id", "result": None})
    else:
        return jsonify({"code": 2222, "message": "token信息错误", "result": None})


@system.route('/system_manage/system/edit', methods=["PUT"])
def edit_iteration_group_info():
    required_params = ['system_name', 'system_url', 'system_env', 'system_organization_id', 'system_organization_name']
    a = request.get_json()
    res = check(a, required_params)
    header_info = request.headers
    if res is not None:
        msg = "%s是必传字段" % res
        return jsonify({"code": 2222, "message": msg})
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        a = request.get_json()
        user_id = int(token_result)
        system_id = a['id']
        system_name = a['system_name']
        system_url = a['system_url']
        system_env = a['system_env']
        system_organization_id = a['system_organization_id']
        system_organization_name = a['system_organization_name']
        check_id = 'select * from system_url_manage where id=%d and is_delete=0 ' % system_id
        res = db.select_one(check_id)
        if res is None:
            return jsonify({"code": 2222, "message": "无效的id", "result": None})
        else:
            try:
                insert_sql = "update system_url_manage set user_id=%d,system_name='%s',system_url='%s',system_env='%s'," \
                             "system_organization_id='%s',system_organization_name='%s' where id=%d" \
                             % (user_id, system_name, system_url, system_env, system_organization_id,
                                system_organization_name, system_id)
                db.add_one(insert_sql)
                return jsonify({"code": 200, "message": "success", "result": None})
            except:
                db.end()
                return jsonify({"code": 2222, "message": "系统异常"})

    else:
        return jsonify({"code": 2222, "message": "token信息错误", "result": None})


# 全部——条件 查询
@system.route('/system_manage/system/list', methods=["GET"])
def get_iteration_group_list():
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        data_page_size = int(request.args.get("page_size"))
        start = int(request.args.get("page_index"))
        system_name = request.args.get("system_name")
        system_env = request.args.get("system_env")
        start_index = int((start - 1) * data_page_size)
        if system_name == '' and system_env == '':
            total_count_sql = "select count(1) as num from system_url_manage where is_delete = 0 "
            res_num = db.select_one(total_count_sql)
            total_num = res_num["num"]
            if total_num > 0:
                detail_info_sql = "select sm.*,u.user_name from system_url_manage sm " \
                                  "left join users u on sm.user_id=u.id " \
                                  "where sm.is_delete = 0  order by sm.id desc limit %d,%d" %(start_index,data_page_size)

                detail_info = db.select_many(detail_info_sql)
                page_cnt = page_size(total_num, data_page_size)
                return jsonify(
                    {"code": 200,
                     "message": "success",
                     "result": detail_info,
                     "currentPage": start, "pageSize": data_page_size,
                     "totalPage": page_cnt, "total": total_num
                     }
                )
            else:
                return jsonify({"code": 200, "message": "success", "result": [], "total": 0})
        # 查询条件都不为空
        if (system_name and system_env) != '':
            total_count_sql = "select count(1)as num from system_url_manage sm left join users u on sm.user_id=u.id " \
                              "where sm.is_delete = 0 and sm.system_env = '%s' and system_name like '%%%s%%' " \
                              % (system_env, system_name)
            res_num = db.select_one(total_count_sql)
            total_num = res_num["num"]
            if total_num > 0:
                name_info_sql = "select sm.*,u.user_name from system_url_manage sm " \
                                "left join users u on sm.user_id=u.id " \
                              "where sm.is_delete = 0 and sm.system_env = '%s' and system_name like '%%%s%%' " \
                              % (system_env, system_name)
                all_info = db.select_many(name_info_sql)
                page_cnt = page_size(total_num, data_page_size)
                return jsonify(
                    {"code": 200,
                     "message": "success",
                     "result": all_info,
                     "currentPage": start, "pageSize": data_page_size,
                     "totalPage": page_cnt, "total": total_num
                     }
                )
            else:
                return jsonify({"code": 200, "message": "success", "result": [], "total": 0})
        elif system_name != '':
            total_count_sql = "select count(1)as num from system_url_manage sm left join users u on sm.user_id=u.id " \
                              "where sm.is_delete = 0 and sm.iteration_group_name like '%%%s%%' " \
                              % system_name
            res_num = db.select_one(total_count_sql)
            total_num = res_num["num"]
            if total_num > 0:
                name_info_sql = "select sm.*,u.user_name from system_url_manage sm " \
                                "left join users u on sm.user_id=u.id " \
                              "where sm.is_delete = 0 and sm.system_name like '%%%s%%' order by sm.id desc  " \
                              % system_name
                name_info = db.select_many(name_info_sql)
                page_cnt = page_size(total_num, data_page_size)
                return jsonify(
                    {"code": 200,
                     "message": "success",
                     "result": name_info,
                     "currentPage": start, "pageSize": data_page_size,
                     "totalPage": page_cnt, "total": total_num
                     }
                )
            else:
                return jsonify({"code": 200, "message": "success", "result": []})
        elif system_env != '':
            total_count_sql = "select count(1) as num from system_url_manage sm left join users u on sm.user_id=u.id " \
                            "where sm.is_delete = 0 and sm.system_env = '%s' " % system_env
            res_num = db.select_one(total_count_sql)
            total_num = res_num["num"]
            if total_num > 0:
                env_info_sql = "select ig.*,u.user_name from system_url_manage sm " \
                               "left join users u on sm.user_id=u.id " \
                            "where sm.is_delete = 0 and sm.system_env = '%s' order by sm.id desc " % system_env
                env_info = db.select_many(env_info_sql)
                page_cnt = page_size(total_num, data_page_size)
                return jsonify(
                    {"code": 200,
                     "message": "success",
                     "result": env_info,
                     "currentPage": start, "pageSize": data_page_size,
                     "totalPage": page_cnt, "total": total_num
                     }
                )
            else:
                return jsonify({"code": 200, "message": "success", "result": [], "total": 0})
        else:
            return jsonify({"code": 200, "message": "success", "result": [], "total": 0})
    else:
        return jsonify({"code": 2222, "message": "系统异常", "result": None})


# 根据环境——条件 查询
@system.route('/system_manage/system/listByEnv', methods=["GET"])
def get_system_list_by_env():
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        system_env = request.args.get("system_env")
        total_count_sql = "select count(1) as num from system_url_manage where is_delete = 0 and system_env='%s' " \
                          % system_env
        res_num = db.select_one(total_count_sql)
        total_num = res_num["num"]
        if total_num > 0:
            detail_info_sql = "select * from system_url_manage where is_delete = 0 and system_env='%s'" % system_env
            detail_info = db.select_many(detail_info_sql)
            return jsonify(
                {"code": 200,
                 "message": "success",
                 "result": detail_info,
                 "total": total_num
                 }
            )
        else:
            return jsonify({"code": 200, "message": "success", "result": [], "total": 0})
    else:
        return jsonify({"code": 2222, "message": "token信息错误", "result": None})

