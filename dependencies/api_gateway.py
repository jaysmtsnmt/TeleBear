from flask import Flask, request

app = Flask(__name__)
app.debug = False
auth_cred = ""

def clearAuthUri():
    global auth_cred
    auth_cred = ""

# @app.route('/')
# def home():
#     return 'API Gateway'

@app.route('/')
def oauth2callback():
    global auth_cred
    code = request.args.get('code')
    if code == None:
        auth_cred = ""
        return "TeleBear API Gateway. :)"
    
    else:            
        print(request.args)
        print(f"[GATEWAY] Authcode: {code}")
        auth_cred = code
        return f"Please copy and paste this authentication code into the TeleBear: \n{auth_cred}"

def host():
    app.run(port=5000, use_reloader=False)
    