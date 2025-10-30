from flask import Flask, request, render_template, redirect, jsonify
from flask_cors import CORS
import json, os, random, string, time
from ConfigHelper import NighthawhsServerConfig, NighthawksPanelConfig, NhkSniperConfig
import asyncio
from datetime import datetime
import aiohttp

# file paths
license_db_path = os.path.join(os.path.dirname(__file__), "license_db.json")


app = Flask(__name__, template_folder="components")
CORS(app)

# helper functions
async def sendMessageToLog(title, message):
    url = f"https://nhk-discord-notifier.onrender.com/send-panel-log"

    params = {
        "title": title,
        "message": message
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params) as response:
            return "message sent !" if response.status in (200, 204) else "error !"
        

def generate_key(license_type: str, quantity: int):
    keys = []
    for _ in range(quantity):
        metadata = {
            "app_name": "nighthawks_panel",
            "app_version": "V8",
            "license_type": license_type,
            "is_used": False,
            "username": "",
            "password": "",
            "expiry_date": 0
        }

        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        formatted = '-'.join(random_string[i:i+4] for i in range(0, len(random_string), 4))
        full_key = f"NHK-{formatted}"

        keys.append({full_key: metadata})
    return keys


def GenerateLicenseKey(license_type: str, quantity: int):
    allowed_type = ["week", "month"]
    if license_type not in allowed_type:
        return {"message ": "license type is not supported!", "status": 400}

    try:
        keys = generate_key(license_type, quantity)

        # Ensure file exists and is valid
        if not os.path.exists(license_db_path):
            with open(license_db_path, 'w') as f:
                json.dump([], f)

        with open(license_db_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []

        data.extend(keys)

        with open(license_db_path, 'w') as f:
            json.dump(data, f, indent=2)

        return {"message": "License keys generated successfully.", "generated_keys": keys, "status": 200}

    except Exception as e:
        return {"message": str(e), "status": 500}



def RegisterUser(license_key: str, username: str, password: str):
    keys = []
    try:
        with open(license_db_path, 'r') as license_file:
            try:
                data = json.load(license_file)
            except json.JSONDecodeError:
                data = []

        for record in data:
            for k, m in record.items():
                if m['username'] == username:
                    return {"message": "Username is already taken !", "status": 400}
                

            if license_key in record:
                license_data = record[license_key]


                if license_data['is_used']:
                    return {"message": "License key is already used !", "status": 400}
                

                if license_data['license_type'] == "week":
                    expiry_date = int(time.time()) + 7 * 24 * 60 * 60
                elif license_data['license_type'] == "month":
                    expiry_date = int(time.time()) + 30 * 24 * 60 * 60     
                else:
                    return {"message": "Invalid license type !", "status": 400}

        
                # update license key metadata...
                license_data['username'] = username
                license_data['password'] = password
                license_data['is_used'] = True
                license_data['expiry_date'] = expiry_date
                        
                    
                # save json file
                with open(license_db_path, 'w') as updated_file:
                    json.dump(data, updated_file, indent=2)

                return {"message": "Account created successfully.", "status": 200}
        

        return {"message": "Invalid license key !", "status": 400}
    

    except Exception as e:
        return {"message": str(e), "status": 500}


def LoginUser(username: str, password: str):
    attempt_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(license_db_path, 'r') as f:
        data = json.load(f)

    for record in data:
        for key, metadata in record.items():
            if metadata['username'] == username:
                if metadata['password'] == password:
                    if int(time.time()) >= metadata['expiry_date']:
                        asyncio.run(sendMessageToLog("Panel Login Alert", f"License subscription is over, Please contact developer.\nUsername: **{metadata['username']}**\nAttempt: **{attempt_datetime}**"))

                        return {"message": "License is expired !", "status": 400}
                    

                    daysleftMesaage = GetDaysLeftFromExpiryDate(metadata['expiry_date'])
                    asyncio.run(sendMessageToLog("Panel Login Alert", f"Login Success✅\nUsername: **{metadata['username']}**\nExpiry: *{daysleftMesaage['message']}*\nAttempt: **{attempt_datetime}**\nThank you for using our panel."))
                    
                    return {"message": "Login Success", "metadata_response": metadata, "status": 200}
                
                else:
                    asyncio.run(sendMessageToLog("Panel Login Alert", f"Login Blocked ❌, Invalid Password\nUsername: **{metadata['username']}**\nAttempt: **{attempt_datetime}**"))
                    return {"message": "Invalid Password !", "status": 400}

    asyncio.run(sendMessageToLog("Panel Login Alert", f"Login failed ❌, username *{metadata['username']}* not found !\nAttempt: **{attempt_datetime}**"))
    return {"message": "No user found !", "status": 400}



def GetDaysLeftFromExpiryDate(expiryDate: int):
    try:
        get_days_left = int((expiryDate - int(time.time())) / 86400)
        return {"message": f"{get_days_left} days left", "status": 200}
    
    except:
        return {"message": "n/a", "status": 400}



@app.route("/")
def home():
    return redirect("/aimbot-config")


@app.route("/aimbot-config")
def tab_1():
    return render_template("pg_aimbot_config.html")

@app.route("/sniper-config")
def tab_2():
    return render_template("pg_sniper_config.html")


@app.route("/whitelist-service")
def tab_3():
    return render_template("pg_whitelist.html")


@app.route("/authentication-service")
def tab_4():
    return render_template("pg_auth_service.html")


@app.route("/get-aimbot-config")
def get_panel_config():
    try:
        nighthawks_panel_config = NighthawksPanelConfig()
        data = json.dumps(nighthawks_panel_config.__dict__, indent=2)

        return jsonify({'response': data}), 200 
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500



@app.route("/get-sniper-config")
def get_sniper_config():
    try:
        sniper_config = NhkSniperConfig()
        data = json.dumps(sniper_config.__dict__, indent=2)

        return jsonify({"response": data}), 200
    
    except Exception as e:
        return jsonify({"message": str(e)}), 500
        



@app.route("/update-server-status")
def update_server_status():
    server_status = request.args.get("server_status")

    if not server_status:
        return jsonify({'message': "server status is required !"}), 400
    
    try:
        nighthawks_server_config = NighthawhsServerConfig(
            server_status=server_status
        )

        if server_status == "0":
            nighthawks_server_config.update()
            return jsonify({'response': "server is offline"}), 200
        
        elif server_status == "1":
            nighthawks_server_config.update()
            return jsonify({"response": 'server is online'}), 200
        
        else:
            return jsonify({"message": "invalid server status !"}), 400
            

    except Exception as e:
        return jsonify({'message': str(e)}), 500




@app.route("/update-sniper-config")
def update_sniper():
    sniper_scan = request.args.get("scan")
    sniper_replace = request.args.get("replace")

    if not sniper_scan:
        return jsonify({"message": "sniper scan pattern is required !"}), 400
    
    if not sniper_replace:
        return jsonify({"message": "sniper replace pattern is required !"}), 400


    sniper_config = NhkSniperConfig(
        scan_pattern=sniper_scan, 
        replace_pattern=sniper_replace
    )    

    sniper_config.update()

    return jsonify({"message": "Sniper code patched successfully..."}), 200



@app.route("/update-aimbot-config")
def update_configs():
    scan_pattern = request.args.get("scan_pattern")
    write_offset = request.args.get("write_offset")
    head_offset = request.args.get("head_offset")
    left_ear_offset = request.args.get("left_ear_offset")
    right_ear_offset = request.args.get("right_ear_offset")
    left_shoulder_offset = request.args.get("left_shoulder_offset")
    right_shoulder_offset = request.args.get("right_shoulder_offset")


    if not scan_pattern:
        return jsonify({'message': 'scan pattern is required !'}), 400
    
    if not write_offset:
        return jsonify({'message': 'write offset is required !'}), 400
    
    if not head_offset:
        return jsonify({'message': 'head offset is required !'}), 400
    
    if not left_ear_offset:
        return jsonify({'message': 'left ear offset is required !'}), 400
    
    if not right_ear_offset:
        return jsonify({'message': 'right ear offset is required !'}), 400
    
    if not left_shoulder_offset:
        return jsonify({'message': 'left shoulder offset is required !'}), 400
    
    if not right_shoulder_offset:
        return jsonify({'message': 'right shoulder offset is required !'}), 400
    
    try:
        nighthawks_panel_config = NighthawksPanelConfig(
            scan_pattern=scan_pattern,
            write_offset=write_offset,
            head_offset=head_offset,
            left_ear_offset=left_ear_offset,
            right_ear_offset=right_ear_offset,
            left_shoulder_offset=left_shoulder_offset,
            right_shoulder_offset=right_shoulder_offset
        )

        nighthawks_panel_config.update()

        return jsonify({"response": "Panel Configs Updated Successfully."}), 200
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500




@app.route("/api/auth/generate-license")
def generate_license_key():
    license_type = request.args.get("type")
    quantity = request.args.get("quantity")

    if not license_type:
        return jsonify({"message": "license type is required!"}), 400
    if not quantity:
        return jsonify({"message": "quantity is required!"}), 400

    try:
        quantity = int(quantity)
    except ValueError:
        return jsonify({"message ": "quantity must be an integer!"}), 400

    response = GenerateLicenseKey(license_type, quantity)
    return jsonify(response), response['status']

@app.route("/api/inspect/unix")
def get_days_left():
    expiry_date = request.args.get("expiry-date")

    if not expiry_date:
        return jsonify({"message": "expiry date is required !"}), 400
    
    response = GetDaysLeftFromExpiryDate(int(expiry_date))

    return jsonify(response), response['status']



@app.route("/api/auth/register")
def register_user():
    license_key = request.args.get("key")
    username = request.args.get("username")
    password = request.args.get("password")

    if not license_key:
        return jsonify({"message ": "license key is required !"}), 400

    if not username:
        return jsonify({"message ": 'username is required !'}), 400
    
    if not password:
        return jsonify({"message ": "password is required !"}), 400
    

    response = RegisterUser(license_key, username, password)
    return jsonify(response), response['status']


@app.route("/api/auth/login")
def login_user():
    username = request.args.get("username")
    password = request.args.get("password")

    if not username:
        return jsonify({"message ": "username is required !"}), 400
    
    if not password:
        return jsonify({"message ": "password is required !"}), 400
    
    response = LoginUser(username, password)
    return jsonify(response), response['status']


@app.route("/api/info/get-unix-time")
def getUnixTime():
    current_unix_time = int(time.time())
    return jsonify({"message": current_unix_time, "status": 200})

    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

