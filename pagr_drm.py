import json
import urllib.request
import requests
import secrets
import sys
import hashlib
import uuid

DEBUG = True
URL = "http://localhost:3000/pagr_drm.php"
INVALID_RESPONSES = [400, 403, 404]

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
        response.raise_for_status()

        responseText = response.text
        responseStatusCode = response.status_code

    except requests.exceptions.ConnectionError:
        Debug(f"ConnectionError: \"{URL}\" is either down, or unreachable to the network.")
        responseText = "{failure}"
        responseStatusCode = "0"

    Debug(f"{responseStatusCode}: {responseText}")
    return responseText, responseStatusCode

def DRMKeyGenerator():
    return secrets.token_hex(32)

def HardwareID():
    mac = uuid.getnode()
    if (mac >> 40) % 2:
        raise ValueError("MAC address is not available or cannot be used.")
    mac_str = ':'.join(['{:02x}'.format((mac >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
    hardware_id = hashlib.sha256(mac_str.encode()).hexdigest()
    
    return hardware_id

def VerifyResponse(responseStatusCode):
    if responseStatusCode in INVALID_RESPONSES:
        Name()
        print("[Failure] Either the DRM server is down, or the client Internet gateway is unreachable.")
        sys.exit(1)

def Check(drm_key):
    hardwareID = HardwareID()
    json = PrepareJson([["drm_key", drm_key],["hardware_id", hardwareID],])
    # Once this is posted with the DRM key and hardware ID, if it's not
    # registered, register it on the PHP side.
    # If registration is successful, a
    # {10} will be outputted. If an {11} is outputted, there was an error with registration
    responseText, responseStatusCode = Post(json)

    VerifyResponse(responseStatusCode)

    # NOTE: Might have to convert the responseText to JSON or something.

    match responseText:
        #--------------#
        # Registration #
        #--------------#
        case "{1}":
            Debug(f"{responseText}: Correct key \"{drm_key}\", already registered \"{hardwareID}\". Approved.")
            return
        case "{10}":
            Debug(f"{responseText}: Correct key \"{drm_key}\", registration complete \"{hardwareID}\". Approved.")
            return
        case "{11}":
            Debug(f"{responseText}: Correct key \"{drm_key}\", registration failed \"{hardwareID}\". Denied.")
            sys.exit(1)

        #-----------------------------#
        # Overregistered (monkaOmega) #
        #-----------------------------#
        case "{2}":
            Debug(f"{responseText}: Correct key \"{drm_key}\", too many device registrations \"{hardwareID}\". Denied!")
            Debug(f"Possible piracy detected. This incident will be reported.")
            sys.exit(1)

        case "{0}":
            Debug(f"{responseText}: Failed to reach server!")
            sys.exit(1)

        case _:
            print(f"Unknown case detected (multiline):\n\t{responseText}")
            sys.exit(1)

def Debug(message):
    if DEBUG:
        print(f"[DEBUG] {message}")

def Name():
    print("pagr_drm: Protect your software.")
