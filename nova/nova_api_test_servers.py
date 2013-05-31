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

def _launch_instance(**kwargs):
    tenant_id          = kwargs.get('tenant_id', get_tenant_id())
    token_id           = kwargs.get('token_id', get_token_id())
    sName              = kwargs.get('name', DEFAULT_VMNAME)
    sImageRef          = kwargs.get('imageRef', DEFAULT_IMAGE_ID)
    sFlavorRef         = kwargs.get('flavorRef', DEFAULT_FLAVOR_ID)
    sMetadata          = kwargs.get('metadata', {})
    sPersonality       = kwargs.get('personality', [])
    sAvailability_zone = kwargs.get('availability_zone', "")
    scheduler_hints    = kwargs.get('scheduler_hints', "")
    max_count          = kwargs.get('max_count', 1)
    min_count          = kwargs.get('min_count', 1)

    s  = { "server": { "name": sName, "imageRef": sImageRef, "flavorRef": sFlavorRef, 
                       "metadata": sMetadata, "personality": sPersonality, 
                       "max_count": max_count, "min_count" : min_count,
                       "os:scheduler_hints": scheduler_hints,
                       "availability_zone": sAvailability_zone } }

    body    = json.dumps(s)
    headers = { "X-Auth-Token":token_id, "Content-type":"application/json" }
    url     = "/v2/%(tenant_id)s/servers" % locals()

    data = _process_data("POST", url, body, headers)
    dd   = json.loads(data)
    # print json.dumps(dd, indent=2)
    return dd

def launch_instance():
    sPersonalityPath = ""
    sPersonalityContents = base64.b64encode("")
    personality = [ { "path":sPersonalityPath, "contents": sPersonalityContents } ]
    availability_zone = "ubuntu12lts"

    # args = dict(tenant_id=tenant_id,token_id=token_id,
    #             name=name,imageRef=imageRef,flavorRef=flavorRef,
    #             metadata=metadata,personality=personality,
    #             max_count=max_count,min_count=min_count,
    #             availability_zone=availability_zone)
    args = {}

    threads = []
    for i in range(1):
        kwargs = {}
        kwargs.update(args)
        kwargs['name'] = "demo-%d" % i
        t = threading.Thread(target=_launch_instance,kwargs=kwargs)
        threads.append(t)

    for t in threads:
       t.start()

    for t in threads:
       t.join()


def terminate_instance(server_id):
    tenant_id = get_tenant_id()
    token_id  = get_token_id()

    body    = None
    headers = { "X-Auth-Token":token_id, "Content-type":"application/json" }
    url     = "/v2/%(tenant_id)s/servers/%(server_id)s" % locals()

    data = _process_data("DELETE", url, body, headers)
    if data:
        dd   = json.loads(data)
        print json.dumps(dd, indent=2)

def main():
    #launch_instance()
    #terminate_instance(server_id='7b4ddf38-d54f-4217-897a-8fdb1b8fdfd1')

if __name__ == '__main__':
    main()