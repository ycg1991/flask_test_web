import time
import base64
import hmac
from flask import request, jsonify
import re
token_key = 'gaodunmyun'


def generate_token(user_id):
    """
    @Args:
        key: str (用户给定的key，需要用户保存以便之后验证token,每次产生token时的key 都可以是同一个key)
        expire: int(最大有效时间，单位为s)
    @Return:
        state: str
    """
    key = token_key
    ts_str = str(time.time() + 604800)
    ts_byte = ts_str.encode("utf-8")
    sha1_str = hmac.new(key.encode("utf-8"), ts_byte, 'sha1').hexdigest()
    user_id = str(user_id)
    token = ts_str + ':' + user_id + ':' + sha1_str
    b64_token = base64.urlsafe_b64encode(token.encode("utf-8"))
    return b64_token.decode("utf-8")


def certify_token(token):
    """
    @Args:
        key: str
        token: str
    @Returns:
        boolean
    """
    key = token_key
    # 对token64位解码
    try:
        token_str = base64.urlsafe_b64decode(token).decode('utf-8')
    except ValueError:
        return 'false'
    # print(token_str)
    # 对解码后的token进行分隔字符串
    token_list = token_str.split(':')
    print(token_list)
    # 分割出的列表长度!=2 说明token不对
    if len(token_list) != 3:
        return 'false'
    # token有效期
    ts_str = token_list[0]
    # print(ts_str)
    # token已过期的情况
    try:
        float(ts_str)
        if float(ts_str) > time.time():
            pass
        else:
            return 'false'
    except ValueError:
        return 'false'
    # 拿到的加密后的密文
    receive_sha1_str = token_list[2]
    # print(receive_sha1_str)
    # 计算根据key加密后的密文
    sha1 = hmac.new(key.encode("utf-8"), ts_str.encode('utf-8'), 'sha1')
    calc_sha1_str = sha1.hexdigest()
    # print(calc_sha1_str)
    # 2个密文一样
    if calc_sha1_str != receive_sha1_str:
        # token 验证失败
        return 'false'
    else:
        # token 验证成功
        user_id = int(token_list[1])
        return user_id



