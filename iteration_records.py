# _*_ coding:utf-8 _*_
# _*_ author:yangchenguang _*_
from flask import request, jsonify
from flask import Blueprint
from generate_token import certify_token
from db_connection import MysqlClient
from io import BytesIO
import xlsxwriter
from common import check, page_size, gen_sql, gen_sql_count, send_ready_message
iteration_records = Blueprint('iteration_records', __name__)
db = MysqlClient()


@iteration_records.route('/iteration_manage/record/create', methods=["POST"])
def new_iteration_record():
    required_params = ['iteration_group_id', 'iteration_version_id',
                       'iteration_story_id', 'iteration_story_type', 'iteration_story_content', 'unittest_status',
                       'iteration_mysql', 'iteration_effect', 'develop_person', 'remark']
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
        iteration_group_id = a['iteration_group_id']
        iteration_version_id = a["iteration_version_id"]
        iteration_story_id = int(a["iteration_story_id"])
        iteration_story_type = a["iteration_story_type"]
        iteration_story_content = a ["iteration_story_content"]
        unittest_status = a["unittest_status"]
        iteration_mysql = a["iteration_mysql"]
        iteration_effect = a["iteration_effect"]
        develop_person = a["develop_person"]
        mark = a["remark"]

        id_check_sql = 'select iteration_version from iterations where id = %d and is_delete =0  limit 1' \
                       % iteration_version_id
        res = db.select_one(id_check_sql)
        check_group_sql = "select iteration_group_name, group_push_address from iteration_groups " \
                          "where id = %d and is_delete=0 limit 1 " % iteration_group_id
        res_name = db.select_one(check_group_sql)
        if res and res_name:
            version = res['iteration_version']
            user_info_sql = "select user_name from users  where id= %d and is_delete =0 " % user_id
            message_info = db.select_one(user_info_sql)
            address = res_name['group_push_address']
            user_name = message_info['user_name']
            group_name = res_name['iteration_group_name']
            insert_sql = "insert into iteration_submit_records (iteration_group_id,iteration_version_id," \
                         "iteration_story_id,iteration_story_type,iteration_story_content,unittest_status," \
                         "iteration_mysql,iteration_effect,develop_person,mark,user_id) " \
                         "values(%d, %d, %d, '%s','%s','%s','%s','%s','%s','%s',%d)" \
                         % (iteration_group_id, iteration_version_id, iteration_story_id, iteration_story_type,
                            iteration_story_content, unittest_status, iteration_mysql, iteration_effect,
                            develop_person, mark, user_id)
            try:
                cnt = db.execute(insert_sql)
                if cnt == 1:
                    db.commit()
                    status_code = send_ready_message(address, group_name, version, iteration_story_id,
                                                     iteration_story_content, iteration_story_type, unittest_status,
                                                     develop_person, user_name, iteration_mysql, iteration_effect,
                                                     mark)
                    if status_code == 200:
                        return jsonify({"code": 200, "message": "success", "result": None})
                    else:
                        return jsonify({"code": 2222, "message": "消息发送失败", "result": None})
                else:
                    return jsonify({"code": 2222, "message": "记录插入异常"})
            except:
                db.end()
                return jsonify({"code": 2222, "message": "系统异常"})

        else:
            return jsonify({"code": 2222, "message": "无效的迭代信息", "result": None})
    else:
        return jsonify({"code": 2222, "message": "token信息错误", "result": None})


# 更新冒烟结果
@iteration_records.route('/iteration_manage/submitSmokeResult', methods=["PUT"])
def update_smoke_result():
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        a = request.get_json()
        smoke_user_id = int(token_result)
        iteration_record_id = a['id']
        smoke_mark = a['smoke_mark']
        smoke_result = a['smoke_result']
        user_check_sql = 'select id from users where id = %d limit 1' % smoke_user_id
        res = db.select_one(user_check_sql)
        if res is None:
            return jsonify({"code": 2222, "message": "用户不存在"})
        check_id_sql = "select id,user_id from iteration_submit_records where id = %d and is_delete=0 " % iteration_record_id
        res_id = db.select_one(check_id_sql)
        if res_id:
            if res_id['user_id'] == smoke_user_id:
                return jsonify({"code": 2222, "message": "自己的记录没有权限点击冒烟"})
            elif smoke_mark == '':
                try:
                    update_sql = "update iteration_submit_records set smoke_result =%d ,test_smoke_user_id = %d where id= %d " \
                        % (smoke_result, smoke_user_id, iteration_record_id)
                    db.edit_one(update_sql)
                    return jsonify({"code": 200, "message": "success", "result": None})
                except:
                    return jsonify({"code": 2222, "message": "系统异常", "result": None})
            else:
                try:
                    update_sql = "update iteration_submit_records set smoke_result =%d ,test_smoke_user_id = %d,smoke_mark='%s' " \
                                 "where id= %d " % (smoke_result, smoke_user_id, smoke_mark, iteration_record_id)
                    db.edit_one(update_sql)
                    return jsonify({"code": 200, "message": "success", "result": None})
                except:
                    return jsonify({"code": 2222, "message": "系统异常", "result": None})
        else:
            return jsonify({"code": 2222, "message": "无效的记录id", "result": None})
    else:
        return jsonify({"code": 2222, "message": "token信息错误", "result": None})


# 修改提交记录
@iteration_records.route('/iteration_manage/record/edit', methods=["put"])
def edit_iteration_record_info():
    required_params = ['iteration_group_id', 'iteration_version_id',
                       'iteration_story_id', 'iteration_story_type', 'iteration_story_content', 'unittest_status',
                       'iteration_mysql', 'iteration_effect', 'develop_person', 'remark']
    a = request.get_json()
    res = check(a, required_params)
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        if res is None:
            user_id = int(token_result)
            iteration_group_id = a['iteration_group_id']
            iteration_version_id = a["iteration_version_id"]
            iteration_story_id = int(a["iteration_story_id"])
            iteration_story_type = a["iteration_story_type"]
            iteration_story_content = a ["iteration_story_content"]
            unittest_status = a["unittest_status"]
            iteration_mysql = a["iteration_mysql"]
            iteration_effect = a["iteration_effect"]
            develop_person = a["develop_person"]
            mark = a["remark"]

            id_check_sql = 'select id from iterations where id = %d and is_delete =0  limit 1' % iteration_version_id
            res = db.select_one(id_check_sql)
            if res is None:
                return jsonify({"code": 2222, "message": "无效的迭代版本"})

            check_group_sql = "select id from iteration_groups where id = %d and is_delete=0 " % iteration_group_id
            res_name = db.select_one(check_group_sql)
            if res_name:
                try:
                    insert_sql = "insert into iteration_submit_records (iteration_group_id,iteration_version_id," \
                                 "iteration_story_id,iteration_story_type,iteration_story_content,unittest_status," \
                                 "iteration_mysql,iteration_effect,develop_person,mark,user_id) " \
                                 "values(%d, %d, %d, '%s','%s','%s','%s','%s','%s','%s',%d)" \
                                 % (iteration_group_id, iteration_version_id, iteration_story_id, iteration_story_type,
                                    iteration_story_content, unittest_status, iteration_mysql, iteration_effect,
                                    develop_person, mark, user_id)
                    print(insert_sql)
                    db.add_one(insert_sql)
                    return jsonify({"code": 200, "message": "success", "result": None})
                except:
                    db.end()
                    return jsonify({"code": 2222, "message": "系统异常"})
            else:
                return jsonify({"code": 2222, "message": "无效的迭代小组", "result": None})
        else:
            msg = "%s是必传字段" % res
            return jsonify({"code": 2222, "message": msg})
    else:
        return jsonify({"code": 2222, "message": "token信息错误", "result": None})


# 记录列表
@iteration_records.route('/iteration_manage/record/list', methods=["GET"])
def get_iteration_record_list():
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        data_page_size = int(request.args.get("page_size"))
        start = int(request.args.get("page_index"))
        iteration_group_id = str(request.args.get("iteration_group_id"))
        iteration_version_id = request.args.get("iteration_version_id")
        smoke_result = request.args.get("smoke_result")
        iteration_story_id = request.args.get("iteration_story_id")
        request_data = {
            "r.iteration_group_id": iteration_group_id,
            "r.iteration_version_id": iteration_version_id,
            "r.iteration_story_id": iteration_story_id,
            "r.smoke_result": smoke_result
        }
        total_count_sql = "select count(1) as num from iteration_submit_records where is_delete = 0 "
        res_num = db.select_one(total_count_sql)
        total_num = res_num["num"]
        if total_num > 0:
            # limit_start_num = int(start - 1) * data_page_size
            sql_end = " order by r.id desc "
            sql_start = "select r.*,u.user_name,u2.user_name as smoke_user_name,ig.iteration_group_name,i.iteration_version " \
                        "from iteration_submit_records r left join iteration_groups ig on r.iteration_group_id = ig.id "\
                        "left join iterations i on r.iteration_version_id=i.id "\
                        "left join users u on r.user_id = u.id   " \
                        "left join users u2 on r.test_smoke_user_id =u2.id where r.is_delete=0 "

            sql_find_count = "select count(1) as num from iteration_submit_records r " \
                             "left join iteration_groups ig on r.iteration_group_id = ig.id "\
                             "left join iterations i on r.iteration_version_id=i.id "\
                             "left join users u on r.user_id = u.id   " \
                             "left join users u2 on r.test_smoke_user_id =u2.id where r.is_delete=0 "
            user_count_sql_2 = gen_sql_count(sql_find_count, request_data)
            fin_res_num = db.select_one(user_count_sql_2)
            find_count = fin_res_num['num']
            version_all_info_sql = gen_sql(sql_start, request_data, sql_end, start, data_page_size)
            all_records = db.select_many(version_all_info_sql)
            page_cnt = page_size(total_num, data_page_size)
            if start <= page_cnt:
                return jsonify(
                    {"code": 200,
                     "message": "success",
                     "result": all_records,
                     "currentPage": start, "pageSize": data_page_size,
                     "totalPage": page_cnt, "total": find_count,
                     })
            else:
                return jsonify({"code": 200, "message": "success", "result": [], "total": 0})
        else:
            return jsonify({"code": 200, "message": "success", "result": [], "total": 0})
    else:
        return jsonify({"code": 2222, "message": "token信息错误", "result": None})


# 删除记录
@iteration_records.route('/iteration_manage/record/delete', methods=["put"])
def delete_record():
    header_info = request.headers
    if "Authorization" not in header_info.keys():
        return jsonify({"code": 2222, "message": "缺少token", "result": None})
    token_result = certify_token(header_info["Authorization"])
    if token_result != 'false':
        a = request.get_json()
        record_id = a['id']
        operate_user_id = int(token_result)
        user_id_sql = "select user_id,smoke_result from iteration_submit_records where id=%d and is_delete=0 " % record_id
        info = db.select_one(user_id_sql)
        user_id = info['user_id']
        smoke_result = info['smoke_result']
        if smoke_result == 2:
            if user_id == operate_user_id:
                try:
                    sql_2 = "update iteration_submit_records set is_delete =1,user_id ='%s' where id=%d" \
                        % (operate_user_id,record_id)
                    db.edit_one(sql_2)
                    return jsonify({"code": 200, "message": "success", "result": None})
                except:
                    db.end()
                    return jsonify({"code": 200, "message": "系统异常", "result": None})
            else:
                return jsonify({"code": 2222, "message": "不能删除别人的记录", "result": None})
        else:
            return jsonify({"code": 2222, "message": "已有冒烟结果的记录不能删除", "result": None})
    else:
        return jsonify({"code": 2222, "message": "无效的token"})

# @iteration_records.route('/iteration_manage/record/download', methods=["GET"])
# def download():
#     # 创建IO对象
#     output = BytesIO()
#     # 写excel
#     workbook = xlsxwriter.Workbook(output)  # 先创建一个book，直接写到io中
#     sheet = workbook.add_worksheet('sheet1')
#     sql_field = ""
