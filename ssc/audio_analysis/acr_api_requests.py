import requests
import time
import base64
import hmac
import hashlib
import sys
import os
from ssc.audio_analysis.acrconfig import identify_access_key, identify_access_secret, \
    identify_host, signature_version, account_access_key, account_access_secret, account_host


def sign(string_to_sign, secret):
    return base64.b64encode(
        hmac.new(secret.encode(), string_to_sign.encode(), digestmod = hashlib.sha1)
            .digest())


def identify_audio(audio_file):
    data_type = 'audio'
    http_method = "POST"
    http_uri = "/v1/identify"
    timestamp = time.time()

    string_to_sign = '\n'.join(
        (http_method, http_uri, identify_access_key, data_type, signature_version, str(timestamp)))

    signature = sign(string_to_sign, identify_access_secret)

    f = open(audio_file, "rb")
    sample_bytes = os.path.getsize(sys.argv[1])

    files = {'sample': f}

    data = {'access_key': identify_access_key,
            'sample_bytes': sample_bytes,
            'timestamp': str(timestamp),
            'signature': signature,
            'data_type': data_type,
            "signature_version": signature_version}

    requrl = identify_host + http_uri

    r = requests.post(requrl, files = files, data = data)
    r.encoding = "utf-8"

    res = r.json()

    return res
    # res = r.json()
    # audio_id = base64.b64decode(res["metadata"]["music"][0]["acrid"])
    #
    # return audio_id