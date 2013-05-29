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

# URL
KEYSTONE_URL = "127.0.0.1:5000"
NOVA_API_URL = "127.0.0.1:8774"
GLANCE_URL   = "127.0.0.1:9292"

# DEFAULT
DEFAULT_USERNAME  = "admin"
DEFAULT_PASSWORD  = "password"
DEFAULT_TENANT_ID = "fb7af3299b9546bf9d1b68375053ccf4"
DEFAULT_IMAGE_ID  = "d5c172ea-658a-4ca1-9733-84ca84d1270e"
DEFAULT_FLAVOR_ID = "1"
DEFAULT_VMNAME    = "demo"    

def get_token_id(username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD, tenant_id=DEFAULT_TENANT_ID):
    sUsername = "\"%s\"" % username
    sPassword = "\"%s\"" % password
    sTenantId = "\"%s\"" % tenant_id

    params  = '{"auth":{"passwordCredentials":{"username": %(sUsername)s, "password":%(sPassword)s},\
                      "tenantId":%(sTenantId)s}}' % locals()
    headers = {"Content-Type": "application/json"}

    keystone_conn = httplib.HTTPConnection(KEYSTONE_URL)
    keystone_conn.request("POST", "/v2.0/tokens", params, headers)

    keystone_response  = keystone_conn.getresponse()
    token_data         = json.loads(keystone_response.read())

    access   = token_data.get('access')
    token    = access.get('token')
    token_id = token.get('id')

    keystone_conn.close()
    return token_id

def delete_image(image_id):
    tenant_id = DEFAULT_TENANT_ID
    token_id  = get_token_id()

    body    = None
    headers = { "X-Auth-Token":token_id, "Content-type":"application/json" }

    nova_api_conn = httplib.HTTPConnection(NOVA_API_URL)
    nova_api_conn.request("DELETE", "/v2/%(tenant_id)s/images/%(image_id)s" % locals(), body, headers)

    response = nova_api_conn.getresponse()
    data = response.read()
    if data:
        dd   = json.loads(data)
        nova_api_conn.close()
        print json.dumps(dd, indent=2)

def main():
    delete_image(image_id='d1add363-d7d2-4630-b183-280b2a8334ff')

if __name__ == '__main__':
    main()