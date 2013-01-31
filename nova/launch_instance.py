#!/usr/bin/env python

# liangxiaoping 2013/01/26 add

import httplib
import json
import base64

import logging

log_format = '%(asctime)s %(levelname)s %(thread)d %(module)s %(funcName)s %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG, filename='elbtest.log')

def get_token_id(username, password, tenant_id, keystone_url):
    sUsername = "\"%s\"" % username
    sPassword = "\"%s\"" % password
    sTenantId= "\"%s\"" % tenant_id

    params  = '{"auth":{"passwordCredentials":{"username": %(sUsername)s, "password":%(sPassword)s},\
                      "tenantId":%(sTenantId)s}}' % locals()
    headers = {"Content-Type": "application/json"}

    keystone_conn = httplib.HTTPConnection(keystone_url)
    keystone_conn.request("POST", "/v2.0/tokens", params, headers)

    keystone_response  = keystone_conn.getresponse()
    token_data         = json.loads(keystone_response.read())

    access   = token_data.get('access')
    token    = access.get('token')
    token_id = token.get('id')

    keystone_conn.close()

    return token_id

def launch_instance(args):
    tenant_id          = args.get('tenant_id')
    token_id           = args.get('token_id')
    
    sName              = args.get('name')
    sImageRef          = args.get('imageRef')
    sFlavorRef         = args.get('flavorRef')
    sMetadata          = args.get('metadata')
    sPersonality       = args.get('personality')
    sAvailability_zone = args.get('availability_zone')

    max_count          = args.get('max_count')
    min_count          = args.get('min_count')
    vm_type            = args.get('vm_type')

    s  = { "server": { "name": sName, "imageRef": sImageRef, "flavorRef": sFlavorRef, "metadata": sMetadata,\
           "personality": sPersonality, "max_count": max_count, "min_count" : min_count, "vm_type":vm_type,
           "availability_zone": sAvailability_zone} }
    sj = json.dumps(s)

    params = sj
    headers = { "X-Auth-Token":token_id, "Content-type":"application/json" }

    print params

    nova_api_url  = args.get('nova_api_url')
    nova_api_conn = httplib.HTTPConnection(nova_api_url)
    nova_api_conn.request("POST", "/v2/%(tenant_id)s/servers" % locals(), params, headers)

    response = nova_api_conn.getresponse()
    data = response.read()
    dd   = json.loads(data)

    nova_api_conn.close()

    print json.dumps(dd, indent=2)
    return dd


def main():
    # User info
    username  = "admin"
    password  = "password"
    tenant_id = "7215b554553741118e186cca0f486db1"  # ELBTEST

    # Get token id
    keystone_url = "10.23.54.150:5000"
    token_id     = get_token_id(username, password, tenant_id, keystone_url)
    print "Your token is: %s" % token_id

    # Launch instance
    nova_api_url  = "10.23.54.150:8774"

    name        = "ELBTEST-VM-Test"
    imageRef    = "9ae50cb0-209a-42e9-88ba-0efba0a59d0f" # Centos6_2-AS-new
    flavorRef   = "1" # autodeploying(14)

    metadata = {}
    sPersonalityPath = ""
    sPersonalityContents = ""
    personality = [ { "path":sPersonalityPath, "contents":base64.b64encode( sPersonalityContents ) } ]

    max_count = "1"
    min_count = "1"

    lb_type = "single"
    vm_type = "vm"

    availability_zone = "myzone:node-154"

    args = dict(tenant_id=tenant_id,token_id=token_id,
                name=name,imageRef=imageRef,flavorRef=flavorRef,
                metadata=metadata,personality=personality,
                max_count=max_count,min_count=min_count,
                lb_type=lb_type,vm_type=vm_type,
                availability_zone=availability_zone,
                nova_api_url=nova_api_url)

    print args

    launch_instance(args)

if __name__ == '__main__':
    main()