# This function an HTTP starter function for Durable Functions.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable activity function (default name is "Hello")
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt
 
import logging,json

from azure.storage.blob import (
    BlockBlobService,
    BlobPermissions,
)
import azure.functions as func
import azure.durable_functions as df
from datetime import date,datetime,timedelta

from . import util
async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    try:
        metadata, file, valid_file = util.get_file(req)
        if not valid_file:
            return func.HttpResponse(json.dumps({'message':'File is invalid'}), status_code=400)    
        block_blob_service = BlockBlobService(account_name="frtrainingstorage001",account_key="uYwwjEgKml/k8UxtW/DRaGE7ILMYJSWH4YyCRLPFDvYi0+0UXHTs4EeBAgBuYxT4SHiBWIwk/NL7csNq0mU6Sw==")
        today = date.today()
        folder = today.strftime("%d-%m-%Y")
        blobname = folder+"/"+metadata[1] 
        block_blob_service.create_blob_from_stream('landmarkcontainer', blobname, file)
        sas_url = block_blob_service.generate_blob_shared_access_signature('landmarkcontainer',blobname,permission=BlobPermissions.READ,start=datetime.utcnow(),expiry=datetime.utcnow() + timedelta(hours=1))
        file_url = 'https://frtrainingstorage001.blob.core.windows.net/landmarkcontainer/'+blobname+'?'+sas_url
        client = df.DurableOrchestrationClient(starter)
        instance_id = await client.start_new(req.route_params["functionName"], None, {"metadata":metadata,"file_url":file_url})

        logging.info(f"Started orchestration with ID = '{instance_id}'.")
        return client.create_check_status_response(req, instance_id)
    except Exception as e:
        logging.info(f"Exception in process-doc {e}")
        return func.HttpResponse(json.dumps({'message':f'exception due to {e}'}), status_code=500)
