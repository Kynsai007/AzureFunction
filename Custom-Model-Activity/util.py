import azure.functions as func
from PyPDF2 import PdfFileReader, PdfFileWriter
from io import BytesIO
from PIL import Image
import math,requests
import logging,sys,json
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


def get_fields_obj(fields):
    fields = json.loads(fields)
    custom_obj = {}
    for f in fields['fields']:
        if f['fieldType'] == 'string':
            custom_obj[f['fieldKey']] = ''
        else:
            custom_obj[f['fieldKey']] = []
    return custom_obj
    
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


