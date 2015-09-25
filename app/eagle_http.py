#!/usr/bin/env python 

from lxml import etree
# from lxml import objectify
import copy
import requests
import datetime

def get_instantaneous_demand(cloud_id, user_email, user_pw):
    headers = construct_headers(cloud_id, user_email, user_pw)
    # command = compose_root(get_instantaneous_demand, None)
    # xml_fragment = etree.tostring(command, pretty_print=True)

    xml_fragment = "<Command>\n  <Name>get_instantaneous_demand</Name>\n</Command>"
    # print xml_fragment

    return send(xml_fragment, headers)

def construct_headers(cloud_id, user_name, password_):
    # print 'Constructing headers...'
    headers = {
        'Cloud-ID': str(cloud_id),
        'User':str(user_name),
        'Password':str(password_),
        'Connection': 'keep-alive',
    }
    return headers

# def compose_root(command, mac_id):
#     command_base = copy.copy(command)

#     self.command_name.text = command
#     command_base.append(self.command_name)

#     if mac_id is not None:
#         self.mac_id.text = mac_id
#         command_base.append(self.mac_id)

#     #! Option to ask for results in JSON format
#     #! Not yet implemented
#     # if self.json == True:
#     #     print "json"
#     #     self.format_.text = 'JSON'
#     #     command_base.append(self.format_)

#     return command_base

def send(send_data,request_headers):

    #Construct URL
    host = 'https://rainforestcloud.com'
    port = 9445
    rurl = '/cgi-bin/post_manager'
    final_url = host+":"+str(port)+rurl

    #Send request, ignoring HTTPS certificate authentication
    requests.packages.urllib3.disable_warnings()
    req = requests.post(
        url = final_url,
        data = send_data,
        headers = request_headers,
        verify = False
    )
        
    # print final_url
    # print request_headers
    # print send_data
    # print req.text

    #Parse and return the result        
    returned_xml_obj = etree.fromstring(req.text)
    # print etree.tostring(returned_xml_obj, pretty_print=True)

    json_obj = parse_instantaneous_demand_to_json(returned_xml_obj)
    # print json_obj

    return json_obj

def parse_instantaneous_demand_to_json(xml):
    # hex_fields = ['DeviceMacId', 'MeterMacId', 'TimeStamp', 'SummationDelivered', 'SummationReceived', 'Multiplier', 'Divisor', 'DigitsRight', 'DigitsLeft',]
    hex_fields = ['DeviceMacId', 'MeterMacId', 'TimeStamp', 'Demand', 'Multiplier', 'Divisor', 'DigitsRight', 'DigitsLeft',]
    str_fields = ['SuppressLeadingZero']

    j = {}

    for field in hex_fields:
        hex_val = xml.xpath(field+'/text()')[0]
        int_val = int(hex_val, 16)
        j[field] = int_val

    for field in str_fields:
        j[field] = xml.xpath(field+'/text()')[0]

    return j

