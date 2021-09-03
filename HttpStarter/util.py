import azure.functions as func
from io import BytesIO
import logging
import requests
import re
import logging

def get_file(req: func.HttpRequest):
    try:
        try:
            req_body = req.get_json()
        except ValueError:
            # There is a file object
            file = req.files["file"]
            return (file.content_type, file.filename), BytesIO(file.read()), True
        else:
            filepath = req_body.get("filepath")
            res = requests.get(filepath)
            if res.status_code == 200:
                ext = res.headers["content-type"].split(";")[0]
                fname = ""
                if "Content-Disposition" in res.headers.keys():
                    fname = re.findall(
                        "filename=(.+)", res.headers["Content-Disposition"]
                    )[0]
                else:
                    fname = filepath.split("/")[-1]
                return (ext, fname), BytesIO(res.content), True
            else:
                return "", b"", False
    except Exception as e:
        logging.error(f"Exception at util.py {str(e)}")
        return "", b"", False


