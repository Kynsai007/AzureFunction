# This function is not intended to be invoked directly. Instead it will be
# triggered by an HTTP starter function.
# Before running this sample, please:
# - create a Durable activity function (default name is "Hello")
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
import json,ast,sys

import azure.functions as func
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    try:
        file_data = context.get_input()
        use_prebuilt = file_data['use_prebuilt']
        result1 = {}
        result2 = {}
        result3 = {}
        if use_prebuilt == 1:
            result1 = yield context.call_activity('Prebuilt-Model-Activity', json.dumps(file_data))
            logging.info(f"Prebuilt done {result1}")
            if json.loads(result1)['message'] == 'success':
                result2 = yield context.call_activity('Custom-Model-Activity', result1)
                logging.info(f"Custom Done {result2}")
                if json.loads(result2)['message'] == 'success':
                    result3 = yield context.call_activity('Business-Logic-Activity',result2)
                    logging.info(f"Business logic done {result3}")
                    if json.loads(result2)['message'] != 'success':
                        result3 = {"message":"exception in Business Logic Activity"}
                else:
                    result2 = {"message":"exception in Custom Model extraction"}
                    return result2
            else:
                result1 = {"message":"exception in Prebuilt Model extraction"}
                return result1
        else:
            fields = file_data['fields']
            model_id = file_data['model_id']
            supplier_name = file_data['template_name']
            metadata = file_data['metadata']
            file_url = file_data['file_url']
            st_name = file_data['st_name']
            st_key = file_data['st_key']
            fr_key = file_data['fr_key']
            fr_endpoint = file_data['fr_endpoint']
            fr_version = file_data['fr_version']
            ismultiple = file_data['ismultiple']
            business_logic_flow = file_data['business_logic_flow']
            componenttypes = file_data['componenttypes']
            result1 = json.dumps({"message":"success","ocr_text":"","model_info":(model_id,supplier_name),"file_info":(metadata,file_url),"st_info":(st_name,st_key),"fr_info":(fr_endpoint,fr_key,fr_version),"fields":fields,"use_prebuilt":use_prebuilt,"business_logic_flow":business_logic_flow,"componenttypes":componenttypes,"ismultiple":ismultiple})
            result2 = yield context.call_activity('Custom-Model-Activity', result1)
            if json.loads(result2)['message'] == 'success':
                result3 = yield context.call_activity('Business-Logic-Activity',result2)
                if json.loads(result2)['message'] != 'success':
                    result3 = {"message":"exception in Business Logic Activity"}
            else:
                result2 = {"message":"exception in Custom Model extraction"}
                return result2
        return result3
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        logging.info(f"Exception in Orchestrator {e} at {line_number}")
        return {"message":f"exception in Orchestrator, reason {e}","custom_result":{}}
main = df.Orchestrator.create(orchestrator_function)