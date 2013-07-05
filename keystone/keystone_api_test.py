#!/usr/bin/env python

# liangxiaoping 2013/01/26 add

import httplib
import json
import base64
import eventlet
import threading
import logging

# LOG
LOG_FORMAT = '%(asctime)s %(levelname)s %(thread)d %(module)s %(funcName)s %(message)s'
logging.basicConfig(format=LOG_FORMAT, level=logging.DEBUG, filename='test.log')

KEYSTONE_HOST = "127.0.0.1:5000"
NOVA_API_HOST = "127.0.0.1:8774"

# DEFAULT
DEFAULT_USERNAME  = "admin"
DEFAULT_PASSWORD  = "password"
DEFAULT_TENANT_ID = "fb7af3299b9546bf9d1b68375053ccf4"
DEFAULT_IMAGE_ID  = "d5c172ea-658a-4ca1-9733-84ca84d1270e"
DEFAULT_FLAVOR_ID = "1"
DEFAULT_VMNAME    = "demo"

def _process_data(method=None, url=None, body=None, headers=None, host=NOVA_API_HOST):
    conn = httplib.HTTPConnection(host)
    conn.request(method, url, body, headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data

def get_tenant_id():
    return DEFAULT_TENANT_ID

def get_token_id(username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD, tenant_id=DEFAULT_TENANT_ID):
    sUsername = "\"%s\"" % username
    sPassword = "\"%s\"" % password
    sTenantId = "\"%s\"" % tenant_id

    body    = '{"auth":{"passwordCredentials":{"username": %(sUsername)s, "password":%(sPassword)s},\
                      "tenantId":%(sTenantId)s}}' % locals()
    headers = {"Content-Type": "application/json"}
    url     = "/v2.0/tokens"

    token_data = _process_data("POST", url, body, headers, KEYSTONE_HOST)
    token_data = json.loads(token_data)
    access     = token_data.get('access')
    token      = access.get('token')
    token_id   = token.get('id')
    return token_id
    
def get_usertoken_byname(user_name):
    body    = json.dumps({"user_name":user_name})
    headers = { "X-Auth-Token":11121314151617181920, "Content-type":"application/json" }
    url     = "/v2.0/users/get_usertoken_by_name"

    data = _process_data("POST", url, body, headers, KEYSTONE_HOST)

    if data:
        dd   = json.loads(data)
        #print json.dumps(dd, indent=2)
        token_id   = dd.get('token_id')
        return token_id

def get_servers(user_name):
    tenant_id = get_tenant_id()
    #token_id  = get_token_id()
    token_id  = get_usertoken_byname(user_name)

    body    = None
    headers = { "X-Auth-Token":token_id, "Content-type":"application/json" }
    url     = "/v2/%(tenant_id)s/servers" % locals()

    data = _process_data("GET", url, body, headers, NOVA_API_HOST)
    if data:
        dd   = json.loads(data)
        print json.dumps(dd, indent=2)

def fetch(**kwargs):
    get_servers(user_name='admin')

def press_test():
    pool = eventlet.GreenPool(200)
    for i in range(200):
        pool.spawn_n(fetch)

    pool.waitall()

def main():
    #get_usertoken_byname(user_name='demo')
    #get_servers(user_name='admin')
    press_test()

if __name__ == '__main__':
    main()