import logging,os,requests,json

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    tok = req.headers.get('token')
    if tok == 'z8R0aWv1/O1QtaY1fcGjwfZKeRYPZl7lgLowRjcSjyaOUx8gpSIvwA==':
        req_files = req.files.values()
        if len(list(req_files)) > 0: 
            h = {}
            if 'headers' in req.form:
                h = json.loads(req.form['headers'])
            resp = requests.post(url=req.form['url'],files=req.files,headers=h)
        else:
            req_body = req.get_json()
            logging.info(f"request body {req_body}")
            url = req_body['url']
            method = req_body['method']
            body = req_body['body']
            h = req_body['headers']
            if method == 'get':
                resp = requests.get(url=url,headers=h)
            elif method == 'put':
                if body is not None:
                    body = json.dumps(body)
                resp = requests.put(url=url,data=body,headers=h)
            elif method == 'post':
                resp = requests.post(url=url,data=json.dumps(body),headers=h)
            elif method == 'delete':
                resp = requests.delete(url=url,headers=h)
        return func.HttpResponse(json.dumps(resp.json()),status_code=200)
    else:
        return func.HttpResponse("Unauthorized Request",status_code=400)