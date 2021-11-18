# This function an HTTP starter function for Durable Functions.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable activity function (default name is "Hello")
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt
 
import logging,json
import azure.functions as func
import azure.durable_functions as df

async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    try:
        body = req.get_json()
        logging.info(f"Recieved {body}")
        client = df.DurableOrchestrationClient(starter)
        instance_id = await client.start_new(req.route_params["functionName"], None, body)

        logging.info(f"Started orchestration with ID = '{instance_id}'.")
        return client.create_check_status_response(req, instance_id)
    except Exception as e:
        logging.info(f"Exception in process-doc {e}")
        return func.HttpResponse(json.dumps({'message':f'exception in http started,reason : {e}','custom_result':{}}), status_code=500)
