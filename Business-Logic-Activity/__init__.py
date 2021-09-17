# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging,json,sys
from fuzzywuzzy import fuzz
import pandas as pd
from dateutil import parser

def main(name: str) -> any:
    # logging.info(name)
    try:
        data = json.loads(name)
        Bill_of_Lading = data['custom_result']['Bill of Lading']
        Certificate_of_Origin = data['custom_result']['Certificate of Origin']
        Commercial_Invoice = data['custom_result']['Commercial Invoice']
        Summary_Packing_List = data['custom_result']['Summary Packing List']
        df = pd.DataFrame(columns=['Commercial Invoice','Packing list/Summary Packing List','COO','BL/AWB/FCR','Pass/Fail'],index=["Shipper", "Consignee", "Notify1", "ASN Number", "Invoice Number", "Invoice Date", "Quantity, Value, Currency", "Payment Term", "Incoterm", "Country of Origin", "HS Cdoe & Description", "Final Destination", "Shipment Mode", "Packages", "Weight Details", "Consignment Details"])

        #Shipper
        df.at['Shipper','Commercial Invoice'] = Commercial_Invoice['CI_Shipper']
        df.at['Shipper','Packing list/Summary Packing List'] = Summary_Packing_List['SPL_Shipper']
        df.at['Shipper','COO'] = Certificate_of_Origin['COO_Shipper']
        df.at['Shipper','BL/AWB/FCR'] = Bill_of_Lading['BL_Shipper']
        df.at['Shipper','Pass/Fail'] = 'PASS' if any([fuzz.token_sort_ratio(Bill_of_Lading['BL_Shipper'],Certificate_of_Origin['COO_Shipper'])>80,fuzz.token_sort_ratio(Bill_of_Lading['BL_Shipper'],Commercial_Invoice['CI_Shipper'])>80, fuzz.token_sort_ratio(Bill_of_Lading['BL_Shipper'],Summary_Packing_List['SPL_Shipper'])>80]) else 'FAIL'

        #Consignee
        df.at['Consignee','Commercial Invoice'] = Commercial_Invoice['CI_Consignee']
        df.at['Consignee','Packing list/Summary Packing List'] = Summary_Packing_List['SPL_Consignee']
        df.at['Consignee','COO'] = Certificate_of_Origin['COO_Consignee']
        df.at['Consignee','BL/AWB/FCR'] = Bill_of_Lading['BL_Consignee']
        df.at['Consignee','Pass/Fail'] = 'PASS' if any([fuzz.token_sort_ratio(Bill_of_Lading['BL_Consignee'],Certificate_of_Origin['COO_Consignee'])>80,fuzz.token_sort_ratio(Bill_of_Lading['BL_Consignee'],Commercial_Invoice['CI_Consignee'])>80, fuzz.token_sort_ratio(Bill_of_Lading['BL_Consignee'],Summary_Packing_List['SPL_Consignee'])>80]) else 'FAIL'

        #Notify1
        df.at['Notify1','Commercial Invoice'] = Commercial_Invoice['CI_Notify1']
        df.at['Notify1','Packing list/Summary Packing List'] = Summary_Packing_List['SPL_Notify1']
        df.at['Notify1','COO'] = Certificate_of_Origin['COO_Notify1']
        df.at['Notify1','BL/AWB/FCR'] = Bill_of_Lading['BL_Notify1']
        df.at['Notify1','Pass/Fail'] = 'PASS' if any([fuzz.token_sort_ratio(Bill_of_Lading['BL_Notify1'],Certificate_of_Origin['COO_Notify1'])>80,fuzz.token_sort_ratio(Bill_of_Lading['BL_Notify1'],Commercial_Invoice['CI_Notify1'])>80, fuzz.token_sort_ratio(Bill_of_Lading['BL_Notify1'],Summary_Packing_List['SPL_Notify1'])>80]) else 'FAIL'

        #Invoice Number
        df.at['Invoice Number','Commercial Invoice'] = Commercial_Invoice['CI_Inv_Number']
        df.at['Invoice Number','Packing list/Summary Packing List'] = Summary_Packing_List['SPL_Inv_Number']
        df.at['Invoice Number','COO'] = Certificate_of_Origin['COO_Inv_Number']
        # df.at['Invoice Number','BL/AWB/FCR'] = Bill_of_Lading['BL_Number']
        df.at['Invoice Number','Pass/Fail'] = 'PASS' if any([fuzz.token_sort_ratio(Commercial_Invoice['CI_Inv_Number'],Certificate_of_Origin['COO_Inv_Number'])>80,fuzz.token_sort_ratio(Commercial_Invoice['CI_Inv_Number'],Summary_Packing_List['SPL_Inv_Number'])>80]) else 'FAIL'
        
        #ASN Number
        df.at['ASN Number','Commercial Invoice'] = Commercial_Invoice['CI_ASN_Number']
        df.at['ASN Number','Pass/Fail'] = 'PASS' if Commercial_Invoice['CI_ASN_Number']  else 'FAIL'

        #Invoice Date
        df.at['Invoice Date','Commercial Invoice'] = Commercial_Invoice['CI_Inv_Date']
        df.at['Invoice Date','Packing list/Summary Packing List'] = Summary_Packing_List['SPL_Inv_Date']
        df.at['Invoice Date','COO'] = Certificate_of_Origin['COO_Inv_Date']
        df.at['Invoice Date','BL/AWB/FCR'] = Bill_of_Lading['BL_Date']
        try:
            df.at['Invoice Date','Pass/Fail'] = 'PASS' if any([parser.parse(Commercial_Invoice['CI_Inv_Date'])==parser.parse(Summary_Packing_List['SPL_Inv_Date']),parser.parse(Commercial_Invoice['CI_Inv_Date'])==parser.parse(Certificate_of_Origin['COO_Inv_Date'])]) else 'FAIL'
        except Exception as e:
            logging.info(f"{Commercial_Invoice['CI_Inv_Date']},{Summary_Packing_List['SPL_Inv_Date']},{Certificate_of_Origin['COO_Inv_Date']}")
            pass
        
        #Payment Term
        df.at['Payment Term','Commercial Invoice'] = Commercial_Invoice['CI_Payment_Term']
        df.at['Payment Term','Pass/Fail'] = 'PASS' if Commercial_Invoice['CI_Payment_Term']  else 'FAIL'

        
        #Incoterm
        df.at['Incoterm','Commercial Invoice'] = Commercial_Invoice['CI_Incoterm']
        df.at['Incoterm','Pass/Fail'] = 'PASS' if Commercial_Invoice['CI_Incoterm']  else 'FAIL'

        #Country of Origin
        df.at['Country of Origin','Commercial Invoice'] = Commercial_Invoice['CI_Country']
        df.at['Country of Origin','COO'] = Certificate_of_Origin['COO_Country']
        df.at['Country of Origin','Pass/Fail'] = 'PASS' if any([fuzz.token_sort_ratio(Commercial_Invoice['CI_Country'],Certificate_of_Origin['COO_Country'])>80]) else 'FAIL'

        #Final Destination
        df.at['Final Destination','Commercial Invoice'] = Commercial_Invoice['CI_Final_Destination']
        df.at['Final Destination','BL/AWB/FCR'] = Bill_of_Lading['BL_Final_Destination']

        # df.at['Final Destination','Pass/Fail'] = 'PASS' if any([fuzz.token_sort_ratio(Bill_of_Lading['BL_Notify1'],Certificate_of_Origin['COO_Notify1'])>80,fuzz.token_sort_ratio(Bill_of_Lading['BL_Notify1'],Commercial_Invoice['CI_Notify1'])>80, fuzz.token_sort_ratio(Bill_of_Lading['BL_Notify1'],Summary_Packing_List['SPL_Notify1'])>80]) else 'FAIL'


        return df.to_json(orient='index')
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        logging.info(f"Exception in Business Logic {e} at {line_number}")
        return json.dumps({"message":"exception"})
    