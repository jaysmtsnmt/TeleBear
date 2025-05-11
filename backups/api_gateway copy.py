from flask import Flask, request

app = Flask(__name__)
app.debug = False
auth_cred = ""

def clearAuthUri():
    global auth_cred
    auth_cred = ""

@app.route('/')
def oauth2callback():
    global auth_cred
    code = request.args.get('code')
    if code == None:
        auth_cred = ""
        return "TeleBear API Gateway :)"
    
    else:            
        #print(request.args)
        print(f"[GATEWAY] Authcode: {code}")
        auth_cred = code
        return f"Authentication Successful! Please return back to telegram."

def host():
    app.run(port=5000, use_reloader=False)

host()