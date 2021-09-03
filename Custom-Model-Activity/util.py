import azure.functions as func
from PyPDF2 import PdfFileReader, PdfFileWriter
from io import BytesIO
from PIL import Image
import math,requests
import sys
import logging
import logging, ast
from azure.cosmosdb.table.tableservice import TableService
from fuzzywuzzy import fuzz

# table_service = TableService(account_name=os.environ['STORAGE_ACCOUNT_NAME'], account_key=os.environ['STORAGE_ACCOUNT_KEY'])
table_service = TableService(
    account_name="frtrainingstorage001",
    account_key="uYwwjEgKml/k8UxtW/DRaGE7ILMYJSWH4YyCRLPFDvYi0+0UXHTs4EeBAgBuYxT4SHiBWIwk/NL7csNq0mU6Sw==",
)
accepted_inch = 5 * 72
accepted_pixel_max = 8000
accepted_pixel_min = 50
accepted_filesize_max = 50

def preprocess(file_name, file_url, file_type):
    try:
        global accepted_inch, accepted_pixel_max, accepted_pixel_min, accepted_filesize_max
        res = requests.get(file_url)
        file_bytes = BytesIO(res.content)
        if file_type == "application/pdf":
            pdf = PdfFileReader(file_bytes, strict=False)
            if not pdf.isEncrypted:
                dimention = pdf.getPage(0).mediaBox
                writer = PdfFileWriter()
                num_pages = pdf.getNumPages()
                for page_no in range(num_pages):
                    page = pdf.getPage(page_no)
                    if max(dimention[2], dimention[3]) > accepted_inch:
                        logging.info(f"Resizing Pdf {file_name} - Page {page_no+1}")
                        page.scaleBy(
                            accepted_inch / max(int(dimention[2]), int(dimention[3]))
                        )
                    writer.addPage(page)

                tmp = BytesIO()
                writer.write(tmp)
                data = tmp.getvalue()
            else:
                return False, "File is Encrypted"
        else:
            img = Image.open(file_bytes)
            w, h = img.size
            if w <= accepted_pixel_min or h <= accepted_pixel_min:
                # Discard this due to low quality
                logging.info(f"Discard {file_name} due to low quality.")
                return False, f"File is below {accepted_pixel_min}"
            elif w >= accepted_pixel_max or h >= accepted_pixel_max:
                """# resize image"""
                logging.info(f"Resize the Image. {file_name}")
                factor = accepted_pixel_max / max(img.size[0], img.size[1])
                img.thumbnail(
                    (int(img.size[0] * factor), int(img.size[1] * factor)),
                    Image.ANTIALIAS,
                )

            byte_io = BytesIO()
            format = "PNG" if file_type == "png" else "JPEG"
            img.save(byte_io, format)
            data = byte_io.getvalue()
        # Upload to Blob

        """ If Filesize is greater than prescribed reject"""
        if math.ceil(sys.getsizeof(data) / 1024 / 1024) >= accepted_filesize_max:
            logging.info(f"Filesize for {file_name} is more..")
            return False, f"File Size is above {accepted_filesize_max}"
        return True, data
    except Exception as e:
        logging.error(f"Exception in util.py {str(e)}")
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        # logging.info(exc_type, fname, exc_tb.tb_lineno, str(e))
        return False, b""


def identify_supplier_model(ocr_text):
    try:
        suppliers = table_service.query_entities("supplierlist")
        supplier_list = []
        supplier_name = ""
        model_id = ""
        Synonyms_Ratio_Table = {}
        Ratio_Table = {}
        supplier_found_from_syn = False
        template_change = False
        for supplier in suppliers:
            try:
                ast.literal_eval(supplier["Synonyms"])
                supplier_list.append(
                    (supplier["SupplierName"], ast.literal_eval(supplier["Synonyms"]))
                )
            except Exception as e:
                exc = f"Error in synonyms for Supplier:- {supplier['SupplierName']}"
                logging.warning(f"Error in synonium of Supplier:- {supplier['SupplierName']}")
        ocr_text_list = ocr_text.split("#splitter#")
        for k in ocr_text_list:
            for x in supplier_list:
                clean_x = str(x[0]).lower().strip()
                clean_k_text = k.strip()
                if clean_x != "" and clean_x not in Synonyms_Ratio_Table:
                    Synonyms_Ratio_Table[x[0]] = 0
                    for syns in x[1]:
                        if syns != "":
                            if Synonyms_Ratio_Table[x[0]] < fuzz.ratio(
                                syns.strip(), clean_k_text
                            ):
                                Synonyms_Ratio_Table.update(
                                    {x[0]: fuzz.ratio(syns.strip(), clean_k_text)}
                                )
                                if fuzz.ratio(syns.strip(), clean_k_text) == 100:
                                    supplier_found_from_syn = True
                                    supplierConfidenceValue = 100
                                    break
                if supplier_found_from_syn:
                    break
            if supplier_found_from_syn:
                break
        syn_supplier_list_confidence = dict(
            sorted(Synonyms_Ratio_Table.items(), key=lambda item: item[1], reverse=True)
        )
        logging.info(f"Synonym matches {syn_supplier_list_confidence}")
        supplier_name = next(iter(syn_supplier_list_confidence))
        logging.info(f"Got supplier name as {supplier_name}")
        if not supplier_found_from_syn:
            supplierConfidenceValue = syn_supplier_list_confidence[supplier_name]
            if supplierConfidenceValue >= 91:
                supplier_found_from_syn = True
        if not supplier_found_from_syn:
            supplier_found = False
            for k in ocr_text_list:
                for x in supplier_list:
                    clean_x = str(x[0]).lower().strip()
                    clean_k_text = k.strip()
                    if clean_x != "":
                        if clean_x in Ratio_Table:
                            if Ratio_Table[x[0]] < fuzz.ratio(
                                clean_x, clean_k_text.lower()
                            ):
                                Ratio_Table.update(
                                    {x[0]: fuzz.ratio(clean_x, clean_k_text.lower())}
                                )
                                if fuzz.ratio(clean_x, clean_k_text.lower()) == 100:
                                    supplier_found = True
                                    break
                        else:
                            Ratio_Table.update(
                                {
                                    x[0]: fuzz.ratio(
                                        clean_x, clean_k_text.lower()
                                    )
                                }
                            )
                            if fuzz.ratio(clean_x, clean_k_text.lower()) == 100:
                                supplier_found = True
                                break
                    if supplier_found:
                        break
                if supplier_found:
                    break
            supplier_list_confidence = dict(
                sorted(Ratio_Table.items(), key=lambda item: item[1], reverse=True)
            )
            logging.info(f"{supplier_list_confidence} Fuzzywuzzy")
            supplier_name = next(iter(supplier_list_confidence))
            supplier_name = supplier_name.strip()
            supplierConfidenceValue = int(supplier_list_confidence[supplier_name])
            logging.info(f"{supplier_name} first by Fuzzywuzzy")
        if supplierConfidenceValue < 80:
            template_change = True
            supplier_name = ""
            model_id = False
        else:
            supplier_model = table_service.query_entities(
                "supplierlist", filter=f"SupplierName eq '{supplier_name}'"
            )
            # logging.info(f"Got {len(list(supplier_model))}")
            for model in supplier_model:
                model_id = str(model.ModelId).strip()
                break
        logging.info(f"Model id {model_id}")
        return model_id, supplier_name, template_change
    except Exception as e:
        logging.error(f"Exception at util.py {str(e)}")
        return False, "", True
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # logging.info(exc_type, exc_tb.tb_lineno, str(e))
        # return "", ""
