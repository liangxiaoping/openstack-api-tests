#!/usr/bin/env python

# liangxiaoping 2013/01/26 add

import httplib
import json
import eventlet

#import threading
#from time import sleep,ctime

import logging

log_format = '%(asctime)s %(levelname)s %(thread)d %(module)s %(funcName)s %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG, filename='elbtest.log')

def get_token_id(username, password, tenant_id, keystone_url):
    username_str = "\"%s\"" % username
    password_str = "\"%s\"" % password
    tenant_id_str = "\"%s\"" % tenant_id
    tenant_id = "7215b554553741118e186cca0f486db1"

    token_params  = '{"auth":{"passwordCredentials":{"username": %(username_str)s, "password":%(password_str)s},\
                      "tenantId":%(tenant_id_str)s}}' % locals()
    token_headers = {"Content-Type": "application/json"}

    keystone_conn = httplib.HTTPConnection(keystone_url)
    keystone_conn.request("POST", "/v2.0/tokens", token_params, token_headers)

    keystone_response  = keystone_conn.getresponse()
    token_data         = json.loads(keystone_response.read())

    access   = token_data.get('access')
    token    = access.get('token')
    token_id = token.get('id')

    keystone_conn.close()

    return token_id

#def add_vm_to_lbg(tenant_id,token_id,lbg_id,nodes,balancer_api_url):
def add_vm_to_lbg(kwargs):
    logging.debug('Enter')
    
    tenant_id = kwargs.get('tenant_id')
    token_id  = kwargs.get('token_id')
    lbg_id    = kwargs.get('lbg_id')
    nodes     = kwargs.get('nodes')
    balancer_api_url = kwargs.get('balancer_api_url')

    balancer_conn   = httplib.HTTPConnection(balancer_api_url)

    #req_params = '{"lbg_id": %(lbg_id_str)s,"nodes": %(nodes)s}' % locals()
    req_params = {}
    req_params['lbg_id'] = lbg_id
    req_params['nodes']  = nodes
    req_params = json.dumps(req_params)
    
    req_header = {"X-Auth-Token":token_id, "Content-type":"application/json"}

    logging.debug('req_params:%s' % req_params)
    logging.debug('req_header:%s' % req_header)

    balancer_conn.request("POST", "/%(tenant_id)s/loadbalancers/add_vm_to_lbg" % locals(), 
                          req_params, req_header)
    
    balancer_response = balancer_conn.getresponse()

    data = balancer_response.read()
    logging.debug('data:%s' % data)

    rsp_data = json.loads(data)
    balancer_conn.close()

    logging.debug('return')

    return rsp_data

def test(tenant_id,token_id,lbg_id,nodes,balancer_api_url):
    logging.debug('tenant_id:%s' % tenant_id)
    logging.debug('token_id:%s' % token_id)
    logging.debug('lbg_id:%s' % lbg_id)
    logging.debug('nodes:%s' % nodes)
    logging.debug('balancer_api_url:%s' % balancer_api_url)

def main():
    # User info
    username  = "admin"
    password  = "password"
    tenant_id = "7215b554553741118e186cca0f486db1"

    # Get token id
    keystone_url = "10.23.54.150:5000"
    token_id = get_token_id(username, password, tenant_id, keystone_url)
    print "Your token is: %s" % token_id

    # Add vm to lbg
    balancer_api_url  = "10.23.54.150:8181"
    lbg_id = "980b3b22b41945f281a19557003bf902"

    # The nodes to be added to lbgs
    nodes_list = []

    # vm 1
    nodes1  = []
    node1 = {"address":"10.23.54.117","port":"80","vm_id":"b857b576-b208-4753-89cf-34877a0173de"}
    nodes1.append(node1)

    nodes_list.append(nodes1)

    # vm 2
    nodes2  = []
    node2 = {"address":"10.23.54.103","port":"80","vm_id":"edc590fd-0697-4646-9735-0ee9effe33bf"}
    nodes2.append(node2)

    nodes_list.append(nodes2)

    args_base = dict(tenant_id=tenant_id,token_id=token_id,lbg_id=lbg_id,
                     balancer_api_url=balancer_api_url)

    #use eventlet
    args_list = []
    for n in nodes_list:
        kwargs = {}
        kwargs.update(args_base)
        kwargs['nodes'] = n
        args_list.append(kwargs)

    pool = eventlet.GreenPool(2)
    for rsp_data in pool.imap(add_vm_to_lbg, args_list):
        print rsp_data

    # use threading
    #threads = []
    #for n in nodes_list:
    #    kwargs = {}
    #    kwargs.update(args_base)
    #    kwargs['nodes'] = n
    #    t = threading.Thread(target=add_vm_to_lbg,kwargs=kwargs)
    #    threads.append(t)

    #for t in threads:
    #    t.start()

    #for t in threads:
    #    t.join()

    logging.debug('Game over')


if __name__ == '__main__':
    main()