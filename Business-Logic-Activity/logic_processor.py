from datetime import datetime
from dateutil import parser
import re
loc = {}
fields = {}
active_field=""
def process_logic(flow_obj,logic_types,custom_result):
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
            output = getvaluefornode(flow_obj,logic_types,custom_result,s['target'],loc['output']) 
        else:
            logic_script = logic_types[s['type']]
            value = custom_result[s['target'].split("-")[1]]
            format = s['format']
            previous_val = s['value']
            exec(logic_script,{'val':value,'format':format,'previous_val':previous_val,'datetime':datetime,'parser':parser,'re':re},loc)
            output = getvaluefornode(flow_obj,logic_types,custom_result,s['target'],loc['output']) 
    return output

def getvaluefornode(flow_obj,logic_types,custom_result,target,first_node_val):
    global fields,active_field
    sourceobj = list(filter(lambda v : v['source'] == target,flow_obj))
    previous_val = first_node_val
    if len(sourceobj) == 1 and sourceobj[0]['target'].find("Output") != -1:
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
                value = custom_result[s['target'].split("-")[1]]
                format = s['format']
                logic_script = logic_types[s['type']]
                exec(logic_script,{'val':value,'format':format,'previous_val':previous_val,'datetime':datetime,'parser':parser,'re':re},loc)
                getvaluefornode(flow_obj,logic_types,custom_result,s['target'],loc['output'])
    return fields