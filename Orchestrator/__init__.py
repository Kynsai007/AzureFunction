# This function is not intended to be invoked directly. Instead it will be
# triggered by an HTTP starter function.
# Before running this sample, please:
# - create a Durable activity function (default name is "Hello")
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
import json

import azure.functions as func
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    try:
        file_data = context.get_input()
        result3 = {}
        result1 = yield context.call_activity('Pre-Processing', json.dumps(file_data))
        if json.loads(result1)['message'] == 'success':
            result2 = yield context.call_activity('Information-Extractor', result1)
            if json.loads(result2)['message'] == 'success':
                result3 = yield context.call_activity('Business-Logic-Activity', result2)
            else:
                return result2
        else:
            return result1
        return result3
    except Exception as e:
        logging.info(f"Exception in Orchestrator {e}")
        return {"message":"exception"}
main = df.Orchestrator.create(orchestrator_function)