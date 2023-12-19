# -*- coding: utf-8 -*-
"""Skyporten public demo.ipynb

# Velkommen til Skyporten!

Dette er en eksempel-notebook som viser hvordan man kan benytte Skyporten.

Vennligst begrens konsumet av testbøtten til 100 ganger i måneden.

## Oppsett av autentiseringen mot Maskinporten

---
"""

# You will need to install the module jwcrypto
# !pip install jwcrypto

# Notebook depends on having the file privatekey.pem present
# This private key is the corresponding one registered in Maskinporten

# NOTE: This should be done outside the notebook, ie. with env-params or secret store

# private_key = """-----BEGIN PRIVATE KEY-----
# MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDOjuX3rPDmQb2d
# [...redacted...]
# 3nUYNk+R8kTbPr0mS5tL2vDZ8gg0xLI70K0FjGneIwL/BtP/XIU4BahVc4NXJZUO
# eZU10Dtmwva8Qi3Drv5hD6Hs
# -----END PRIVATE KEY-----"""

# with open("privatekey.pem", "w") as file:
#    file.write(private_key)

import requests
import uuid
from jwcrypto import jwk, jwt
from datetime import datetime, timezone

audience = "https://skyporten.entur.org"
scope = "entur:skyporten.demo"
client_id = "0429aed4-82f0-11ee-b962-0242ac120002"  # non-existing client_id as example
keyname = "999paabbcc"  # non-existing keyname as example

# Variables from integration
kid = keyname
integration_id = client_id

# Environment specific variables
maskinporten_audience = "https://test.sky.maskinporten.no"
maskinporten_token = "https://test.sky.maskinporten.no/token"

timestamp = int(datetime.now(timezone.utc).timestamp())

with open("privatekey.pem", "r") as file:
    secret = file.read()

key = jwk.JWK.from_pem(
    data=bytes(secret, "ascii"),
    # password=str('PASSWORD').encode() <-- if password needed
)


jwt_header = {"alg": "RS256", "kid": kid}

jwt_claims = {
    "aud": maskinporten_audience,
    "iss": integration_id,
    "scope": scope,
    "resource": audience,
    "iat": timestamp,
    "exp": timestamp + 100,
    "jti": str(uuid.uuid4()),
}

jwt_token = jwt.JWT(
    header=jwt_header,
    claims=jwt_claims,
)
jwt_token.make_signed_token(key)
signed_jwt = jwt_token.serialize()

body = {
    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
    "assertion": signed_jwt,
}

res = requests.post(maskinporten_token, data=body)
skyporten_auth = res.json()["access_token"]
with open("tmp_maskinporten_token.txt", "w") as file:
    file.write(skyporten_auth)

"""## Uthenting fra bøtte"""


# This is information from supplier
GOOGLE_PROJECT_NUM = "207740593944"
GOOGLE_PROJECT_ID = "ent-data-sdsharing-ext-dev"
WORKLOAD_IDENTITY_POOL_ID = "skyporten-public-demo"
WORKLOAD_IDENTITY_POOL_PROVIDER_ID = "skyporten-test"
SERVICE_ACCOUNT_EMAIL = (
    f"skyporten-public-demo-consumer@{GOOGLE_PROJECT_ID}.iam.gserviceaccount.com"
)
BUCKET = "skyporten-public-demo"


json_config_info = {
    "type": "external_account",
    "audience": f"//iam.googleapis.com/projects/{GOOGLE_PROJECT_NUM}/locations/global/workloadIdentityPools/{WORKLOAD_IDENTITY_POOL_ID}/providers/{WORKLOAD_IDENTITY_POOL_PROVIDER_ID}",
    "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
    "token_url": "https://sts.googleapis.com/v1/token",
    "credential_source": {"file": "tmp_maskinporten_token.txt"},
    "service_account_impersonation_url": f"https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/{SERVICE_ACCOUNT_EMAIL}:generateAccessToken",
}

from google.cloud import storage
from google.auth import identity_pool

credentials = identity_pool.Credentials.from_info(json_config_info)

storage_client = storage.Client(project=GOOGLE_PROJECT_ID, credentials=credentials)
list(storage_client.list_blobs(BUCKET))
