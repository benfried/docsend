from docsend import DocSend
import functions_framework
import flask

from io import BytesIO
from requests_html import HTMLSession

@functions_framework.http
def docsend_http(request: flask.Request) -> flask.typing.ResponseReturnValue:
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The docsend URL converted to PDF (application/pdf)
                Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_args = request.args
    email = False
    passcode = False

    if request_args and "id" in request_args:
        id = request_args["id"]
        if "email" in request_args:
            email = request_args["email"]
        if "passcode" in request_args:
            passcode = request_args["passcode"]
    else:
        return 'Must pass id={docsendid} and usually email={email}', 400
            
    ds = DocSend(id)
    ds.fetch_meta()
    if email:
        if passcode: 
            ds.authorize(email, passcode)
        else:
            ds.authorize(email)
    else:
        return 'email not specified', 400
    
    ds.fetch_images()

    byte_io = BytesIO()

    ds.save_pdf(byte_io)

    byte_io.seek(0)

    response = flask.make_response(byte_io.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    return response


