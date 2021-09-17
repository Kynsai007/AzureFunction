# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging,json,os,sys
from . import util
from . import formrecognizer
def main(name: str) -> str:
    custom_fields = {'Bill of Lading':{'BL_Shipper':'','BL_Consignee':'','BL_Notify1':'','BL_Notify2':'','BL_Number':'','BL_Date':'','BL_Final_Destination':'','BL_Table_Details':[]},'Certificate of Origin':{'COO_Shipper':'','COO_Notify1':'','COO_Notify2':'','COO_Consignee':'','COO_Number':'','COO_Date':'','COO_Country':'','COO_Inv_Number':'','COO_Inv_Date':'','COO_Table_Details':[]},'Commercial Invoice':{'CI_Shipper':'','CI_Consignee':'','CI_Notify1':'','CI_Notify2':'','CI_ASN_Number':'','CI_Number':'','CI_Date':'','CI_Payment_Term':'','CI_Incoterm':'','CI_Country':'','CI_Final_Destination':'','CI_Inv_Number':'','CI_Inv_Date':'','CI_Table_Details':[]},'Summary Packing List':{'SPL_Shipper':'','SPL_Consignee':'','SPL_Notify1':'','SPL_Notify2':'','SPL_Inv_Number':'','SPL_Inv_Date':'','SPL_Table_Details':[],'SPL_Table_Details_1':[]}}
    supplier_name = ''    
    ocr_text = ''
        
    try:
        model_data = json.loads(name)
        ocr_text = model_data['ocr_text']
        model_info = model_data['model_info']
        model_id = model_info[0]
        supplier_name = model_info[1]
        file_data = model_data['file_info']
        metadata = file_data[0]
        file_url = file_data[1] 
        st_info = model_data['st_info']
        fr_info = model_data['fr_info']
        fr_endpoint = fr_info[0]
        fr_key = fr_info[1]
        fr_version = fr_info[2]   
        status, body = util.preprocess(metadata[1], file_url, metadata[0])

        if not status:
            return {"message": "Failed in pre-process", "result": {}, "status_code":400}
        fr_headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
            "Content-Type": metadata[0],
            "Ocp-Apim-Subscription-Key": fr_key,
        }
        url = f"{fr_endpoint}/formrecognizer/{fr_version}/custom/models/{model_id}/analyze?includeTextDetails=false"
        custom_result = formrecognizer.getOCRText(url,fr_headers,body)
        custom_fields = {'Bill of Lading':{'BL_Shipper':'','BL_Consignee':'','BL_Notify1':'','BL_Notify2':'','BL_Number':'','BL_Date':'','BL_Final_Destination':'','BL_Table_Details':[]},'Certificate of Origin':{'COO_Shipper':'','COO_Notify1':'','COO_Notify2':'','COO_Consignee':'','COO_Number':'','COO_Date':'','COO_Country':'','COO_Inv_Number':'','COO_Inv_Date':'','COO_Table_Details':[]},'Commercial Invoice':{'CI_Shipper':'','CI_Consignee':'','CI_Notify1':'','CI_Notify2':'','CI_ASN_Number':'','CI_Number':'','CI_Date':'','CI_Payment_Term':'','CI_Incoterm':'','CI_Country':'','CI_Final_Destination':'','CI_Inv_Number':'','CI_Inv_Date':'','CI_Table_Details':[]},'Summary Packing List':{'SPL_Shipper':'','SPL_Consignee':'','SPL_Notify1':'','SPL_Notify2':'','SPL_Inv_Number':'','SPL_Inv_Date':'','SPL_Table_Details':[],'SPL_Table_Details_1':[]}}
        CustomdocumentResults = custom_result["analyzeResult"]["documentResults"]
        for item in CustomdocumentResults:
            fields = item['fields']
            
            #Bill of Lading
            if "BL_Shipper" in fields:
                if "text" in fields['BL_Shipper']:
                    custom_fields['Bill of Lading']['BL_Shipper'] = fields['BL_Shipper']['text']
            if "BL_Consignee" in fields:
                if "text" in fields['BL_Consignee']:
                    custom_fields['Bill of Lading']['BL_Consignee'] = fields['BL_Consignee']['text']
            if "BL_Notify1" in fields:
                if "text" in fields['BL_Notify1']:
                    custom_fields['Bill of Lading']['BL_Notify1'] = fields['BL_Notify1']['text']
            if "BL_Notify2" in fields:
                if "text" in fields['BL_Notify2']:
                    custom_fields['Bill of Lading']['BL_Notify2'] = fields['BL_Notify2']['text']
            if "BL_Number" in fields:
                if "text" in fields['BL_Number']:
                    custom_fields['Bill of Lading']['BL_Number'] = fields['BL_Number']['text']
            if "BL_Date" in fields:
                if "text" in fields['BL_Date']:
                    custom_fields['Bill of Lading']['BL_Date'] = fields['BL_Date']['text']
            if "BL_Final_Destination" in fields:
                if "text" in fields['BL_Final_Destination']:
                    custom_fields['Bill of Lading']['BL_Final_Destination'] = fields['BL_Final_Destination']['text']
            
            #Certificate of Origin
            if "COO_Shipper" in fields:
                if "text" in fields['COO_Shipper']:
                    custom_fields['Certificate of Origin']['COO_Shipper'] = fields['COO_Shipper']['text']
            if "COO_Notify1" in fields:
                if "text" in fields['COO_Notify1']:
                    custom_fields['Certificate of Origin']['COO_Notify1'] = fields['COO_Notify1']['text']
            if "COO_Notify2" in fields:
                if "text" in fields['COO_Notify2']:
                    custom_fields['Certificate of Origin']['COO_Notify2'] = fields['COO_Notify2']['text']
            if "COO_Consignee" in fields:
                if "text" in fields['COO_Consignee']:
                    custom_fields['Certificate of Origin']['COO_Consignee'] = fields['COO_Consignee']['text']
            if "COO_Number" in fields:
                if "text" in fields['COO_Number']:
                    custom_fields['Certificate of Origin']['COO_Number'] = fields['COO_Number']['text']
            if "COO_Date" in fields:
                if "text" in fields['COO_Date']:
                    custom_fields['Certificate of Origin']['COO_Date'] = fields['COO_Date']['text']
            if "COO_Country" in fields:
                if "text" in fields['COO_Country']:
                    custom_fields['Certificate of Origin']['COO_Country'] = fields['COO_Country']['text']
            if "COO_Inv_Number" in fields:
                if "text" in fields['COO_Inv_Number']:
                    custom_fields['Certificate of Origin']['COO_Inv_Number'] = fields['COO_Inv_Number']['text']
            if "COO_Inv_Date" in fields:
                if "text" in fields['COO_Inv_Date']:
                    custom_fields['Certificate of Origin']['COO_Inv_Date'] = fields['COO_Inv_Date']['text']
            
            #Commercial Invoice
            if "CI_Shipper" in fields:
                if "text" in fields['CI_Shipper']:
                    custom_fields['Commercial Invoice']['CI_Shipper'] = fields['CI_Shipper']['text']
            if "CI_Consignee" in fields:
                if "text" in fields['CI_Consignee']:
                    custom_fields['Commercial Invoice']['CI_Consignee'] = fields['CI_Consignee']['text']
            if "CI_Notify1" in fields:
                if "text" in fields['CI_Notify1']:
                    custom_fields['Commercial Invoice']['CI_Notify1'] = fields['CI_Notify1']['text']
            if "CI_Notify2" in fields:
                if "text" in fields['CI_Notify2']:
                    custom_fields['Commercial Invoice']['CI_Notify2'] = fields['CI_Notify2']['text']
            if "CI_ASN_Number" in fields:
                if "text" in fields['CI_ASN_Number']:
                    custom_fields['Commercial Invoice']['CI_ASN_Number'] = fields['CI_ASN_Number']['text']
            if "CI_Number" in fields:
                if "text" in fields['CI_Number']:
                    custom_fields['Commercial Invoice']['CI_Number'] = fields['CI_Number']['text']
            if "CI_Date" in fields:
                if "text" in fields['CI_Date']:
                    custom_fields['Commercial Invoice']['CI_Date'] = fields['CI_Date']['text']
            if "CI_Payment_Term" in fields:
                if "text" in fields['CI_Payment_Term']:
                    custom_fields['Commercial Invoice']['CI_Payment_Term'] = fields['CI_Payment_Term']['text']
            if "CI_Incoterm" in fields:
                if "text" in fields['CI_Incoterm']:
                    custom_fields['Commercial Invoice']['CI_Incoterm'] = fields['CI_Incoterm']['text']
            if "CI_Country" in fields:
                if "text" in fields['CI_Country']:
                    custom_fields['Commercial Invoice']['CI_Country'] = fields['CI_Country']['text']
            if "CI_Final_Destination" in fields:
                if "text" in fields['CI_Final_Destination']:
                    custom_fields['Commercial Invoice']['CI_Final_Destination'] = fields['CI_Final_Destination']['text']
            if "CI_Inv_Number" in fields:
                if "text" in fields['CI_Inv_Number']:
                    custom_fields['Commercial Invoice']['CI_Inv_Number'] = fields['CI_Inv_Number']['text']
            if "CI_Inv_Date" in fields:
                if "text" in fields['CI_Inv_Date']:
                    custom_fields['Commercial Invoice']['CI_Inv_Date'] = fields['CI_Inv_Date']['text']
            
            #Summary Packing List
            if "SPL_Shipper" in fields:
                if "text" in fields['SPL_Shipper']:
                    custom_fields['Summary Packing List']['SPL_Shipper'] = fields['SPL_Shipper']['text']
            if "SPL_Consignee" in fields:
                if "text" in fields['SPL_Consignee']:
                    custom_fields['Summary Packing List']['SPL_Consignee'] = fields['SPL_Consignee']['text']
            if "SPL_Notify1" in fields:
                if "text" in fields['CI_Inv_Date']:
                    custom_fields['Summary Packing List']['SPL_Notify1'] = fields['SPL_Notify1']['text']
            if "SPL_Notify2" in fields:
                if "text" in fields['SPL_Notify2']:
                    custom_fields['Summary Packing List']['SPL_Notify2'] = fields['SPL_Notify2']['text']
            if "SPL_Inv_Number" in fields:
                if "text" in fields['SPL_Inv_Number']:
                    custom_fields['Summary Packing List']['SPL_Inv_Number'] = fields['SPL_Inv_Number']['text']
            if "SPL_Inv_Date" in fields:
                if "text" in fields['SPL_Inv_Date']:
                    custom_fields['Summary Packing List']['SPL_Inv_Date'] = fields['SPL_Inv_Date']['text']
            
            #Tabular Data
            if "BL_Table_Details" in fields:
                if len(fields['BL_Table_Details']['valueArray']) > 0:
                    custom_fields['Bill of Lading']['BL_Table_Details'] = [{h:None if 'text' not in k['valueObject'][h] else k['valueObject'][h]['text'] for h in k['valueObject'].keys()} for k in fields['BL_Table_Details']['valueArray']]
            if "CI_Table_Details" in fields:
                if len(fields['CI_Table_Details']['valueArray']) > 0:
                    custom_fields['Commercial Invoice']['CI_Table_Details'] = [{h:None if 'text' not in k['valueObject'][h] else k['valueObject'][h]['text'] for h in k['valueObject'].keys()} for k in fields['CI_Table_Details']['valueArray']]
                        
            
            if "SPL_Table_Details" in fields:
                if len(fields['SPL_Table_Details']['valueArray']) > 0:
                    custom_fields['Summary Packing List']['SPL_Table_Details'] = [{h:None if 'text' not in k['valueObject'][h] else k['valueObject'][h]['text'] for h in k['valueObject'].keys()} for k in fields['SPL_Table_Details']['valueArray']]
            
            if "SPL_Table_Details_1" in fields:
                if len(fields['SPL_Table_Details_1']['valueArray']) > 0:
                    custom_fields['Summary Packing List']['SPL_Table_Details_1'] = [{h:None if 'text' not in k['valueObject'][h] else k['valueObject'][h]['text'] for h in k['valueObject'].keys()} for k in fields['SPL_Table_Details_1']['valueArray']]
            
            if "COO_Table_Details" in fields:
                if len(fields['COO_Table_Details']['valueArray']) > 0:
                    custom_fields['Certificate of Origin']['COO_Table_Details'] = [{h:None if 'text' not in k['valueObject'][h] else k['valueObject'][h]['text'] for h in k['valueObject'].keys()} for k in fields['COO_Table_Details']['valueArray']]
            
            
            return json.dumps({"message":"success","custom_result":custom_fields,"ocr_text":ocr_text,"supplier_name":supplier_name})
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        logging.info(f"Exception in Imformation Extraction {e} - {line_number}")
        return json.dumps({"message":"failure in information extraction","custom_result":custom_fields,"ocr_text":ocr_text,"supplier_name":supplier_name})