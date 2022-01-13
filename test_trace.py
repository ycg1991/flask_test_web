# _*_ coding:utf-8 _*_
# _*_ author:yangchenguang _*_

from flask import Flask, request, session, g, jsonify
import config
import time
import pymysql
import send_mail
from flask import Blueprint
test = Blueprint('test', __name__)


@test.route('/test/ready/submit', methods=['post'])
def test_ready():
    cursor = None
    try:
        a = request.get_json()
        user_id = a['user_id']
        sys_name = a['sys_name']
        sys_url = a['sys_url']
        sys_env = a['sys_env']
        update_time = time.strftime("%Y-%m-%d %H:%m:%S", time.localtime())
        send_mail.ready_test_mail(a)
        cursor = config.db.cursor(pymysql.cursors.DictCursor)
        sql = 'insert into nav (sys_name,sys_env,sys_url,user_id,update_time) values("%s","%s","%s","%s","%s")' \
            % (sys_name, sys_env, sys_url, user_id, update_time)
        cursor.execute(sql)
        config.db.commit()
        return jsonify({"code": 200, "message": "success", "data": "ok"})
    finally:
        cursor.close()


@test.route('/test/ready/get', methods=['get'])
def get_records():
    pass
