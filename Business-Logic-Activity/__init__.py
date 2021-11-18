# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging,json,sys
from . import logic_processor

def main(name: str) -> str:
    data = json.loads(name)
    custom_result = data['custom_result']
    try:
        business_logic_flow = json.loads(data['business_logic_flow'])
        components = data['componenttypes']
        logging.info(f"business_logic {type(business_logic_flow)}, components : {type(components)}, custom_fields : {type(custom_result)}")
        custom_result = logic_processor.process_logic(business_logic_flow,components,custom_result)
        return json.dumps({"message":"success","custom_result":custom_result})
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        logging.info(f"Exception in Business Logic {e} - {line_number}")
        return json.dumps({"message":f"exception in business logic, reason: {e}","custom_result":custom_result})