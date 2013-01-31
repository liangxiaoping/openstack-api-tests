#!/usr/bin/env python

# liangxiaoping 2013/01/26 add


import httplib
import json
import urllib

## make sure that osuser is set to your actual username, "admin"
## works for test installs on virtual machines, but it's a hack
osuser = "root"
## use something else than "shhh" for your password
ospassword = "njyanfa"

# admin user
username = "\"admin\""
password = "\"password\""

# admin tenant id
tenant_id_str = "\"60e5f88c5f234818904583d47175b2c5\""
tenant_id = "60e5f88c5f234818904583d47175b2c5"

# get token
keystone_url = "10.23.54.150:5000"
token_params  = '{"auth":{"passwordCredentials":{"username": %(username)s, "password":%(password)s}, "tenantId":%(tenant_id_str)s}}'\
          % locals()
token_headers = {"Content-Type": "application/json"}

keystone_conn = httplib.HTTPConnection(keystone_url)
keystone_conn.request("POST", "/v2.0/tokens", token_params, token_headers)

keystone_response  = keystone_conn.getresponse()
token_data         = json.loads(keystone_response.read())

access   = token_data.get('access')
token    = access.get('token')
token_id = token.get('id')

print "Your token is: %s" % token_id
keystone_conn.close()

# get floating ip
instance_uuid = "c5494b96-7ce0-463b-80a6-91463df7eefc"
nova_api_url  = "10.23.54.150:8774"
nova_conn     = httplib.HTTPConnection(nova_api_url)

req_params    = urllib.urlencode({})
req_header    = { "X-Auth-Token":token_id, "Content-type":"application/json" }

nova_conn.request("GET", "/v2/%(tenant_id)s/servers/%(instance_uuid)s/floating_ip" % locals(), req_params, req_header)
nova_response = nova_conn.getresponse()

rsp_data      = json.loads(nova_response.read())
nova_conn.close()

print rsp_data

