# _*_ coding:utf-8 _*_
# _*_ author:yangchenguang _*_
from flask import request, jsonify
from flask import Blueprint
from generate_token import certify_token
from db_connection import MysqlClient
from io import BytesIO
import xlsxwriter
from common import check, page_size, gen_sql, gen_sql_count, send_ready_message
feedback = Blueprint('feedback_record', __name__)
db = MysqlClient()


@feedback.route('/feedback/record/create', methods=["POST"])
def new_feedback_record():
    required_params = ['title', 'description', 'platform', 'iteration_group_id', 'important_level', 'feedback_time',
                       'feedback_deal_type', 'agency_type', 'feedback_user', 'feedback_classify', 'function_module']
    a = request.get_json()
    res = check(a, required_params)
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    if res is not None:
        msg = "%s是必传字段" % res
        return jsonify({"code": 2222, "message": msg})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        user_id = token_result
        title = a['title']
        description = a["description"]
        iteration_group_id = int(a["iteration_group_id"])
        platform = a["platform"]
        important_level = a["important_level"]
        feedback_time = a["feedback_time"]
        agency_type = a["agency_type"]
        function_module = a["function_module"]
        feedback_classify = int(a['feedback_classify'])
        feedback_deal_type = a["feedback_deal_type"]
        feedback_user = a["feedback_user"]
        influence = a['influence']
        mark = a["mark"]
        check_group_sql = "select  id from iteration_groups " \
                          "where id = %d and is_delete=0 limit 1 " % iteration_group_id
        res_group = db.select_one(check_group_sql)
        if res_group:
            insert_sql = "insert into feedback_records (title,description,iteration_group_id,platform,important_level" \
                         ",feedback_time,function_module,feedback_classify,feedback_deal_type,agency_type," \
                         "influence,mark,feedback_user,user_id)" \
                         "values('%s', '%s',%d, '%s', '%s','%s','%s',%d,'%s','%s','%s','%s','%s',%d)" \
                         % (title, description, iteration_group_id, platform, important_level,feedback_time,
                            function_module, feedback_classify, feedback_deal_type,
                            agency_type, influence,mark, feedback_user, user_id)
            print(insert_sql)
            try:
                db.add_one(insert_sql)
                return jsonify({"code": 200, "message": "success", "result": None})
            except:
                db.end()
                return jsonify({"code": 2222, "message": "系统异常"})

        else:
            return jsonify({"code": 2222, "message": "无效的团队,请更换", "result": None})
    else:
        return jsonify({"code": 2222, "message": "token信息错误", "result": None})


# 记录列表
@feedback.route('/feedback/record/list', methods=["GET"])
def get_feed_record_list():
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        data_page_size = int(request.args.get("page_size"))
        start = int(request.args.get("page_index"))
        total_count_sql = "select count(1) as num from feedback_records where is_delete = 0 "
        res_num = db.select_one(total_count_sql)
        total_num = res_num["num"]
        if total_num > 0:
            start_index = int((start - 1) * data_page_size)
            sql_all = "select f.*,u.user_name,ig.iteration_group_name from feedback_records f " \
                      "left join iteration_groups ig on f.iteration_group_id = ig.id "\
                      "left join users u on f.user_id = u.id   " \
                      " where f.is_delete=0 order by f.id desc limit %d,%d " % (start_index, data_page_size)
            all_records = db.select_many(sql_all)
            page_cnt = page_size(total_num, data_page_size)
            if start <= page_cnt:
                return jsonify(
                    {"code": 200,
                     "message": "success",
                     "result": all_records,
                     "currentPage": start, "pageSize": data_page_size,
                     "totalPage": page_cnt, "total": total_num,
                     })
            else:
                return jsonify({"code": 200, "message": "success", "result": [], "total": 0})
        else:
            return jsonify({"code": 200, "message": "success", "result": [], "total": 0})
    else:
        return jsonify({"code": 2222, "message": "token信息错误", "result": None})


@feedback.route('/feedback/record/delete', methods=["PUT"])
def delete_record():
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        a = request.get_json()
        user_id = token_result
        record_id = a['id']
        if record_id is None:
            return jsonify({"code": 2222, "message": "id不能为空"})
        # 检查id是否有效
        check_id_sql = "select id,user_id from feedback_records where id = %d and is_delete=0" % record_id
        res = db.select_one(check_id_sql)
        if res:
            if user_id != res['user_id']:
                return jsonify({"code": 2222, "message": "非本人创建的不能删除", "result": None})
            else:
                update_sql = "update feedback_records set is_delete =1 where id= %d " % record_id
                db.edit_one(update_sql)
            return jsonify({"code": 200, "message": "success", "result": None})
        else:
            return jsonify({"code": 2222, "message": "无效的id", "result": None})
    else:
        return jsonify({"code": 2222, "message": "token信息错误", "result": None})


# 状态流转
@feedback.route('/feedback/record/updateStatus', methods=["POST"])
def update_record_status():
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        a = request.get_json()
        user_id = token_result
        record_id = a['id']
        record_status = a['feedback_status_new']
        complete_time = a['complete_time']
        feedback_deal_user = a['feedback_deal_user']
        if record_id is None:
            return jsonify({"code": 2222, "message": "id不能为空"})
        # 检查id是否有效
        check_id_sql = "select id,user_id from feedback_records where id = %d and is_delete=0" % record_id
        res = db.select_one(check_id_sql)
        if res:
            if user_id != res['user_id']:
                return jsonify({"code": 2222, "message": "非本人创建的不能操作", "result": None})
            else:
                update_sql = "update feedback_records set feedback_status =%d,complete_time='%s'," \
                             "feedback_deal_user='%s' where id= %d " % (record_status,complete_time,feedback_deal_user,record_id)
                print(update_sql)
                db.edit_one(update_sql)
            return jsonify({"code": 200, "message": "success", "result": None})
        else:
            return jsonify({"code": 2222, "message": "无效的id", "result": None})
    else:
        return jsonify({"code": 2222, "message": "token信息错误", "result": None})
