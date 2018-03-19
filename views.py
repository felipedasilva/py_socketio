import json
import models

async def process_login(session, msg):
    try:
        email = msg['params']['email']
        password = msg['params']['password']
    except Exception:
        return json.dumps(u'{"status": "error", "detail": "Invalid params", "msg": "' + msg['msg']
                                      + '"}')
    try:
        user = await models.User.authenticate(email, password)
    except Exception:
        return factory_response(msg['msg'], 'error', 'Error in the server')
    if user:
        session.set_user(user)
        user = user.get_json_data()
        return json.dumps('{"status": "success", "detail": "User authenticated", "data": ' + user
                          + ', "msg": "' + msg['msg'] + '"}')
    return json.dumps('{"status": "error", "detail": "Invalid credentials", "msg": "' + msg['msg']
                                  + '"}')


async def process_create_user(session, msg):
    try:
        name = msg['params']['name']
        email = msg['params']['email']
        password = msg['params']['password']
    except Exception:
        return factory_response(msg['msg'], 'error', 'Invalid params')
    try:
        user = await models.User.signup(name, email, password)
    except Exception as e:
        print('errrrrrror')
        print(e)
        return factory_response(msg['msg'], 'error', 'Error in the server')
    return factory_response(msg['msg'], 'success', 'User created', user.public_data())


async def process_list_all_users(session, msg):
    users = await models.User.select('id', 'name', 'email').gino.all()
    return factory_response(msg['msg'], 'success', 'Users', [dict(user) for user in users])


def factory_response(msg, status, detail, data=None):
    response = {
        'status': status,
        'detail': detail,
        'msg': msg
    }
    if data:
        response['data'] = data
    return json.dumps(response).encode()
