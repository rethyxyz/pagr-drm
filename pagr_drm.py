import json
import requests
import secrets
import sys
import hashlib
import uuid

DEBUG = True
URL = "http://localhost:3000/pagr_drm.php"
COMPANY_URL = "https://rethy.xyz/Software/pagr_drm"
INVALID_RESPONSES = [400, 404]

def PrepareJson(pairs):
    data = {}
    for key, value in pairs:
        data[key] = value
    return json.dumps(data)

def Post(data):
    Debug(f"POST data: {data}")

    headers = {'Content-Type': 'application/json'}
    url = URL

    try:
        response = requests.post(url, data=data, headers=headers, timeout=10)
        Debug(f"{response.status_code}: {response.text}")
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        Debug(f"ConnectionError: \"{URL}\" is either down, or unreachable to the network.")
        raise
    except requests.exceptions.HTTPError:
        # We'll handle HTTP errors in the calling function
        pass
    except requests.exceptions.RequestException as e:
        Debug(f"Request Exception: {e}")
        raise

    return response

def DRMKeyGenerator():
    return secrets.token_hex(32)

def HardwareID():
    mac = uuid.getnode()
    if (mac >> 40) % 2:
        raise ValueError("MAC address is not available or cannot be used.")
    mac_str = ':'.join(['{:02x}'.format((mac >> ele) & 0xff)
                        for ele in range(0, 8 * 6, 8)][::-1])
    hardware_id = hashlib.sha256(mac_str.encode()).hexdigest()

    return hardware_id

def Check(drm_key):
    hardwareID = HardwareID()
    json_data = PrepareJson([["drm_key", drm_key], ["hardware_id", hardwareID]])

    try:
        response = Post(json_data)
        response_json = response.json()
        responseStatusCode = response.status_code
    except requests.exceptions.HTTPError as e:
        response = e.response
        responseStatusCode = response.status_code
        try:
            response_json = response.json()
        except ValueError:
            Debug("Invalid JSON response")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        Name()
        print("The DRM server is unreachable. Please ensure your network connection is online and try again.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        Name()
        print(f"Request Exception: {e}")
        sys.exit(1)

    if responseStatusCode in INVALID_RESPONSES:
        Name()
        print("The DRM server is unreachable. Please ensure your network connection is online and try again.")
        sys.exit(1)

    # Process the response JSON
    if 'message' in response_json:
        message = response_json['message']
        status = response_json.get('status', '')

        if message == "Already registered" and status == "approved":
            Debug(f"{message}: Correct key \"{drm_key}\", already registered \"{hardwareID}\". Approved.")
            return
        elif message == "Registration complete" and status == "approved":
            Debug(f"{message}: Correct key \"{drm_key}\", registration complete \"{hardwareID}\". Approved.")
            return
        else:
            print(f"Unknown success response: {response_json}")
            sys.exit(1)
    elif 'error' in response_json:
        error = response_json['error']
        status = response_json.get('status', '')

        if error == "Invalid DRM key":
            Name()
            print("Invalid DRM key detected.")
            print(f"Please purchase this software from {COMPANY_URL}.")
            sys.exit(1)
        elif error == "Too many devices registered" and status == "denied":
            Debug(f"{error}: Correct key \"{drm_key}\", too many device registrations \"{hardwareID}\". Denied!")
            Debug("Possible piracy detected. This incident will be reported.")
            sys.exit(1)
        elif error == "Registration failed" and status == "denied":
            Debug(f"{error}: Correct key \"{drm_key}\", registration failed \"{hardwareID}\". Denied.")
            sys.exit(1)
        else:
            print(f"Unknown error response: {response_json}")
            sys.exit(1)
    else:
        print(f"Unexpected response: {response_json}")
        sys.exit(1)

def Debug(message):
    if DEBUG:
        print(f"[DEBUG] {message}")

def Name():
    print("pagr_drm: Protect your software.")
