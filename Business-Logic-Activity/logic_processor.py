from datetime import datetime
from dateutil import parser
import re
loc = {}
fields = {}
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
            exec(logic_script,{'val':value,'format':format,'previous_val':previous_val,'datetime':datetime,'parser':parser,'re':re},loc)
            output = getvaluefornode(flow_obj,logic_types,custom_result,s['target'],loc['output'],ismultiple) 
        else:
            logic_script = logic_types[s['type']]
            if ismultiple == False:
                value = custom_result[s['target'].split("-")[1]]
            else:
                for k,v in custom_result.items():
                    if s['target'].split("-")[1] in custom_result[k].keys():
                        value = custom_result[k][s['target'].split("-")[1]]
            format = s['format']
            previous_val = value
            exec(logic_script,{'val':value,'format':format,'previous_val':previous_val,'datetime':datetime,'parser':parser,'re':re},loc)
            output = getvaluefornode(flow_obj,logic_types,custom_result,s['target'],loc['output'],ismultiple) 
    return output

def getvaluefornode(flow_obj,logic_types,custom_result,target,first_node_val,ismultiple):
    global fields,active_field,active_key
    sourceobj = list(filter(lambda v : v['source'] == target,flow_obj))
    previous_val = first_node_val
    if len(sourceobj) == 1 and sourceobj[0]['target'].find("Output") != -1:
        if ismultiple == True:
            for k,v in custom_result.items():
                fields[k] = {}
                if active_field in custom_result[k].keys():
                    fields[k][active_field] = previous_val
        else:
            fields[active_field] = previous_val
    else:
        for s in sourceobj:
            if s['type'] != 'field':
                value = s['value']
                format = s['format']
                logic_script = logic_types[s['type']]
                exec(logic_script,{'val':value,'format':format,'previous_val':previous_val,'datetime':datetime,'parser':parser,'re':re},loc)
                getvaluefornode(flow_obj,logic_types,custom_result,s['target'],loc['output'])
            else:
                active_field = s['target'].split("-")[1]
                if ismultiple == False:
                    value = custom_result[s['target'].split("-")[1]]
                else:
                    for k,v in custom_result.items():
                        if s['target'].split("-")[1] in custom_result[k].keys():
                            value = custom_result[k][s['target'].split("-")[1]]
                format = s['format']
                logic_script = logic_types[s['type']]
                exec(logic_script,{'val':value,'format':format,'previous_val':previous_val,'datetime':datetime,'parser':parser,'re':re},loc)
                getvaluefornode(flow_obj,logic_types,custom_result,s['target'],loc['output'])
    return fields