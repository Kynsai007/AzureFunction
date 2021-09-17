# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging,json,os
from . import util
from . import formrecognizer

def main(name: str) -> str:
    try:
        file_data = json.loads(name)
        metadata = file_data['metadata']
        file_url = file_data['file_url']    
        st_name = file_data['st_name']
        st_key = file_data['st_key']
        fr_key = file_data['fr_key']
        fr_endpoint = file_data['fr_endpoint']
        fr_version = file_data['fr_version']
        fr_doctype = file_data['fr_doctype']
        status, body = util.preprocess(metadata[1], file_url, metadata[0])

        if not status:
            return {"message": "Failed in pre-process", "result": {}, "status_code":400}
        fr_headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
            "Content-Type": metadata[0],
            "Ocp-Apim-Subscription-Key":  fr_key,
        }
        url = f"{fr_endpoint}formrecognizer/{fr_version}/prebuilt/{fr_doctype}/analyze?includeTextDetails=true"
        prebuilt_result = formrecognizer.getOCRText(url,fr_headers,body)
        ocr_text = "#splitter#".join([k["text"].replace('"', '') for i in prebuilt_result[
                                            "analyzeResult"]['readResults'] if 'lines' in i for k in i['lines']])
        model_id, supplier_name, template_change = util.identify_supplier_model(ocr_text,st_name,st_key)
        
        return json.dumps({"message":"success","ocr_text":ocr_text,"model_info":(model_id,supplier_name,template_change),"file_info":(metadata,file_url),"st_info":(st_name,st_key),"fr_info":(fr_endpoint,fr_key,fr_version)})
    except Exception as e:
        logging.info(f"Exception in Pre-Processing {e}")
        return json.dumps({"message":"failure in pre-processing","ocr_text":""})
