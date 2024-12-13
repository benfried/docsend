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
        if request.method == 'POST':
            url = request.form.get('url')
            email = request.form.get('email')
            passcode = request.form.get('passcode')

            if not url or not url.startswith("https://docsend.com/view/"):
                return 'Invalid URL. Must start with "https://docsend.com/view/".', 400

            id = url.split("view/")[1]
        else:
            return '''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>docsend to PDF converter</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            margin: 50px;
                        }
                        h1 {
                            text-align: center;
                        }
                        form {
                            max-width: 500px;
                            margin: auto;
                        }
                        label {
                            display: block;
                            font-size: 1.2em;
                            margin-bottom: 10px;
                        }
                        input[type="text"], input[type="password"] {
                            width: 100%;
                            padding: 10px;
                            margin-bottom: 20px;
                            box-sizing: border-box;
                        }
                        input[type="submit"] {
                            display: block;
                            width: 100%;
                            padding: 10px;
                            background-color: #4CAF50;
                            color: white;
                            border: none;
                            cursor: pointer;
                        }
                        input[type="submit"]:hover {
                            background-color: #45a049;
                        }
                    </style>
                </head>
                <body>
                    <h1>docsend to PDF converter</h1>
                    <form method="post">
                        <label for="url">URL (the whole URL, beginning with https://docsend.com/view):</label>
                        <input type="text" id="url" name="url"><br>
                        <label for="email">Email the docsend was shared with:</label>
                        <input type="text" id="email" name="email"><br>
                        <label for="passcode">Passcode (if one was given):</label>
                        <input type="password" id="passcode" name="passcode"><br>
                        <input type="submit" value="Submit">
                    </form>
                </body>
                </html>
            ''', 200

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
    response.headers['Content-Disposition'] = f"attachment; filename=docsend_{id}.pdf"
    return response


