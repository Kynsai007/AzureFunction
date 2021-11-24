# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging,json,os,sys,ast
from . import util
from . import formrecognizer
def main(name: str) -> str:
    model_data = json.loads(name)
    custom_fields = json.loads(model_data['fields'])
    supplier_name = ''    
    ocr_text = ''
    business_logic_flow = []
    componenttypes = {}
    try:
        ocr_text = model_data['ocr_text']
        model_info = model_data['model_info']
        model_id = model_info[0]
        supplier_name = model_info[1]
        file_data = model_data['file_info']
        metadata = file_data[0]
        file_url = file_data[1] 
        st_info = model_data['st_info']
        use_prebuilt = model_data['use_prebuilt']
        business_logic_flow = model_data['business_logic_flow']
        componenttypes= model_data['componenttypes']
        ismultiple = model_data['ismultiple']
        fr_info = model_data['fr_info']
        fr_endpoint = fr_info[0]
        fr_key = fr_info[1]
        fr_version = fr_info[2]   
        status, body = util.preprocess(metadata[1], file_url, metadata[0])
        if not status:
            return json.dumps({"message": "exception in custom model data capture, reason: Fail in custom preprocess", "result": {}, "status_code":400})
        fr_headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
            "Content-Type": metadata[0],
            "Ocp-Apim-Subscription-Key": fr_key,
        }
        url = f"{fr_endpoint}/formrecognizer/{fr_version}/custom/models/{model_id}/analyze?includeTextDetails=false"
        if use_prebuilt == 0:
            url = f"{fr_endpoint}/formrecognizer/{fr_version}/custom/models/{model_id}/analyze?includeTextDetails=true"
        custom_result = formrecognizer.getOCRText(url,fr_headers,body)
        if use_prebuilt == 0:
            ocr_text = "#splitter#".join([k["text"].replace('"', '') for i in custom_result["analyzeResult"]['readResults'] if 'lines' in i for k in i['lines']])
        CustomdocumentResults = custom_result["analyzeResult"]["documentResults"]
        logging.info(f"Custom data {CustomdocumentResults}")
        for item in CustomdocumentResults:
            fields = item['fields']
            #Text Fields
            if ismultiple == False:
                for key, value in custom_fields.items():
                    if key in fields:
                        if value == "":
                            if "text" in fields[key]:
                                custom_fields[key] = fields[key]['text']
                        else:
                            if len(fields[key]['valueArray']) > 0:
                                custom_fields[key] = [{h:None if 'text' not in k['valueObject'][h] else k['valueObject'][h]['text'] for h in k['valueObject'].keys()} for k in fields[key]['valueArray']]
            else:
                for key, value in custom_fields.items():
                    for k,v in custom_fields[key].items():
                        if k in fields:
                            if v == "":
                                if "text" in fields[k]:
                                    custom_fields[key][k] = fields[key]['text']
                            else:
                                if len(fields[k]['valueArray']) > 0:
                                    custom_fields[key][k] = [{h:None if 'text' not in k['valueObject'][h] else k['valueObject'][h]['text'] for h in k['valueObject'].keys()} for k in fields[key]['valueArray']]               
        
        logging.info(f"Custom fields {custom_fields}")
        return json.dumps({"message":"success","custom_result":custom_fields,"ocr_text":ocr_text,"template_name":supplier_name,"business_logic_flow":business_logic_flow,"componenttypes":componenttypes,"ismultiple":ismultiple})
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        logging.info(f"Exception in Custom Model Activity {e} - {line_number}")
        return json.dumps({"message":f"exception in custom model data capture, reason: {e}","custom_result":custom_fields,"ocr_text":ocr_text,"template_name":supplier_name,"business_logic_flow":business_logic_flow,"componenttypes":componenttypes})