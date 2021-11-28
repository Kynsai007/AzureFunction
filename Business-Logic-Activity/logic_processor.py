from datetime import datetime
import logging
from dateutil import parser
from fuzzywuzzy import fuzz
import re
loc = {}
fields = {}
fieldsarr = []
active_field=""
active_key = ""
def process_logic(flow_obj,logic_types,custom_result,ismultiple):
    global loc
    output = {}
    sourceobj = list(filter(lambda v : v['source'] == 'source',flow_obj))
    for s in sourceobj:
        if s['type'] != 'field':
            logic_script = logic_types[s['type']]
            value = s['value']
            format = s['format']
            previous_val = s['value']
            name = ''
            if 'name' in s:
                name = s['name']
            if s['type'] == 'Comparator':
                value = value.split(",")[:-1]
                temp = {}
                if ismultiple == True:
                    for k,v in custom_result.items():
                        for val in value:
                            if val in custom_result[k].keys():
                                temp[val] = {'value':custom_result[k][val],'key':k}
                else:
                    for k,v in custom_result.items():
                        temp[k] = {'value':v}
                value = temp
            exec(logic_script,{'val':value,'format':format,'previous_val':previous_val,'datetime':datetime,'parser':parser,'re':re,'fuzz':fuzz,'name':name},loc)
            output = getvaluefornode(flow_obj,logic_types,custom_result,s['target'],loc['output'],ismultiple) 
        else:
            logic_script = logic_types[s['type']]
            value = custom_result[s['target'].split("-")[1]]
            format = s['format']
            name = ''
            if 'name' in s:
                name = s['name']
            previous_val = value
            exec(logic_script,{'val':value,'format':format,'previous_val':previous_val,'datetime':datetime,'parser':parser,'re':re,'fuzz':fuzz,'name':name},loc)
            output = getvaluefornode(flow_obj,logic_types,custom_result,s['target'],loc['output'],ismultiple) 
    return output

def getvaluefornode(flow_obj,logic_types,custom_result,target,first_node_val,ismultiple):
    global fields,active_field,active_key,fieldsarr
    sourceobj = list(filter(lambda v : v['source'] == target,flow_obj))
    previous_val = first_node_val
    logging.info(f"sourceobj {sourceobj}")
    logging.info(f"prev {previous_val}")
    
    if len(sourceobj) == 0 and ismultiple == True:
        fieldsarr.append(previous_val)
        
    if len(sourceobj) == 1 and sourceobj[0]['target'].find("Output") != -1:
        fields[active_field] = previous_val
    else:
        for s in sourceobj:
            if s['type'] != 'field':
                value = s['value']
                format = s['format']
                logic_script = logic_types[s['type']]
                name = ''
                if 'name' in s:
                    name = s['name']
                if s['type'] == 'Comparator':
                    value = value.split(",")[:-1]
                    temp = {}
                    if ismultiple == True:
                        for k,v in custom_result.items():
                            for val in value:
                                if val in custom_result[k].keys():
                                    temp[val] = {'value':custom_result[k][val],'key':k}
                    else:
                        for k,v in custom_result.items():
                            temp[k] = {'value':v}
                    value = temp
                exec(logic_script,{'val':value,'format':format,'previous_val':previous_val,'datetime':datetime,'parser':parser,'re':re,'fuzz':fuzz,'name':name},loc)
                getvaluefornode(flow_obj,logic_types,custom_result,s['target'],loc['output'],ismultiple)
            else:
                active_field = s['target'].split("-")[1]
                value = custom_result[s['target'].split("-")[1]]
                format = s['format']
                logic_script = logic_types[s['type']]
                name = ''
                if 'name' in s:
                    name = s['name']
                exec(logic_script,{'val':value,'format':format,'previous_val':previous_val,'datetime':datetime,'parser':parser,'re':re,'fuzz':fuzz,'name':name},loc)
                getvaluefornode(flow_obj,logic_types,custom_result,s['target'],loc['output'],ismultiple)
    if ismultiple == True:
        return fieldsarr
    return fields