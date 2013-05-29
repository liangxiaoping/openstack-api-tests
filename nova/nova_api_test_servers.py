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

def _launch_instance(**kwargs):
    tenant_id          = kwargs.get('tenant_id', DEFAULT_TENANT_ID)
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

    nova_api_conn = httplib.HTTPConnection(NOVA_API_URL)
    nova_api_conn.request("POST", "/v2/%(tenant_id)s/servers" % locals(), body, headers)

    response = nova_api_conn.getresponse()
    data = response.read()
    dd   = json.loads(data)

    nova_api_conn.close()
    print json.dumps(dd, indent=2)
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
    tenant_id = DEFAULT_TENANT_ID
    token_id  = get_token_id()

    body    = None
    headers = { "X-Auth-Token":token_id, "Content-type":"application/json" }

    nova_api_conn = httplib.HTTPConnection(NOVA_API_URL)
    nova_api_conn.request("DELETE", "/v2/%(tenant_id)s/servers/%(server_id)s" % locals(), body, headers)

    response = nova_api_conn.getresponse()
    data = response.read()
    if data:
        dd   = json.loads(data)
        nova_api_conn.close()
        print json.dumps(dd, indent=2)

def main():
    #launch_instance()
    #terminate_instance(server_id='7b4ddf38-d54f-4217-897a-8fdb1b8fdfd1')

if __name__ == '__main__':
    main()