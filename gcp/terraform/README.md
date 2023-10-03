# Bruk av workload identity federation med Maskinporten mot GCP



- Login i gcloud `gcloud auth login`
- Gjør klar for terraform
```
export GOOGLE_PROJECT=<dittprosjekt>
```
- `terraform init` og `terraform apply`


```
SUBJECT_TOKEN_TYPE="urn:ietf:params:oauth:token-type:jwt"
SUBJECT_TOKEN=$(cat tmp_token_maskinporten.txt)
PROVIDER_ID=<terraform-provider-id-output>


STS_TOKEN=$(curl https://sts.googleapis.com/v1/token \
    --data-urlencode "audience=//iam.googleapis.com/$PROVIDER_ID" \
    --data-urlencode "grant_type=urn:ietf:params:oauth:grant-type:token-exchange" \
    --data-urlencode "requested_token_type=urn:ietf:params:oauth:token-type:access_token" \
    --data-urlencode "scope=https://www.googleapis.com/auth/cloud-platform" \
    --data-urlencode "subject_token_type=$SUBJECT_TOKEN_TYPE" \
    --data-urlencode "subject_token=$SUBJECT_TOKEN" | jq -r .access_token)
echo $STS_TOKEN


echo $STS_TOKEN > tmp_access_token.txt
export CLOUDSDK_AUTH_ACCESS_TOKEN=$(cat access_token.txt)

gcloud iam service-accounts create some-account-name \
            --display-name="Test account" \
            --project="ent-sdsharing-ext-dev" \
            --access-token-file=tmp_access_token.txt


gcloud auth print-access-token --access-token-file=access_token.txt
```

