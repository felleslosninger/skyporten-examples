# Bruk av workload identity federation med Maskinporten mot GCP



### Login i gcloud with your personal cloud user

```
gcloud auth login
```

### Set google project

```
export GOOGLE_PROJECT=<dittprosjekt>
```

```
gcloud config set project "$GOOGLE_PROJECT"
```


### Create a new workload identity pool

```
export WORKLOAD_POOL_ID=skyportenpoc2

gcloud iam workload-identity-pools create "$WORKLOAD_POOL_ID" \
    --location="global" \
    --description="pool for skyporten poc" \
    --display-name="skyportenpoc try"
```

### Define oidc identity pool provider

```
export ENTUR_AUDIENCE="https://entur.org"
export PROVIDER_ID=skyportenprovider

gcloud iam workload-identity-pools providers create-oidc $PROVIDER_ID \
    --location="global" \
    --workload-identity-pool=$WORKLOAD_POOL_ID \
    --attribute-mapping="attribute.maskinportenscope"="assertion.scope","google.subject"="assertion.consumer.ID","attribute.clientaccess"="\"client::\" + assertion.consumer.ID + \"::\" + assertion.scope" \
    --issuer-uri="https://sky.maskinporten.dev/" \
    --allowed-audiences=$ENTUR_AUDIENCE \
    --description="OIDC identity pool provider for Maskinporten"

```

### Create storage bucket

```
export BUCKET="skyportenbucket2"
gcloud storage buckets create gs://$BUCKET --location="EUROPE-WEST4"
```

### Upload a file

```
echo "bar" > foo.txt
gcloud storage cp foo.txt gs://$BUCKET/foo_remote.txt
Copying file://foo.txt to gs://skyportenbucket/foo_remote.txt
  Completed files 1/1 | 4.0B/4.0B

gcloud storage ls gs://$BUCKET
gs://skyportenbucket/foo_remote.txt
```

### Create a service account and make pool a member

#### Get project number

```
# find proj num in projects list
gcloud projects list

# Export project number
export PROJNUM=[ number ]
```

```
export MASKINPORTENCLIENTID="0192:917422575"
export MASKINPORTENSCOPE="entur:skyss.1"
export SERVICE_ACC='skyportenstorageconsumer'
gcloud iam service-accounts create $SERVICE_ACC \
    --description="Skyporten storage consumer" \
    --display-name="skyportenstoragesa"
```

#### Extract the email from the created SA

```
gcloud iam service-accounts list
skyportenstoragesa                         skyportenstorageconsumer@[project_id].iam.gserviceaccount.com        False

export SAEMAIL="skyportenstorageconsumer@[project_id].iam.gserviceaccount.com"
```

export SAEMAIL="skyportenstorageconsumer@ent-data-sdsharing-ext-dev.iam.gserviceaccount.com"


#### Create policy binding

```
gcloud iam service-accounts add-iam-policy-binding $SAEMAIL \
    --member="principalSet://iam.googleapis.com/projects/$PROJNUM/locations/global/workloadIdentityPools/$WORKLOAD_POOL_ID/attribute.clientaccess/client::$MASKINPORTENCLIENTID::$MASKINPORTENSCOPE" \
    --role="roles/iam.workloadIdentityUser"
```

```
gcloud storage buckets add-iam-policy-binding gs://$BUCKET --member=serviceAccount:$SAEMAIL --role=roles/storage.objectViewer

```

#### Authentication using maskinporten

Logout
`gcloud auth revoke`

Foventer å finne maskinporten-token i full json i `tmp_maskinporten_access_token.json`

```
export MASKINPORTEN_TOKEN_FILE=tmp_maskinporten_token.txt 
cat tmp_maskinporten_access_token.json | jq -r .access_token > $MASKINPORTEN_TOKEN_FILE
export PROVIDER_FULL_IDENTIFIER=projects/${PROJNUM}/locations/global/workloadIdentityPools/$WORKLOAD_POOL_ID/providers/${PROVIDER_ID}

gcloud iam workload-identity-pools create-cred-config $PROVIDER_FULL_IDENTIFIER --service-account=$SAEMAIL --credential-source-file=$MASKINPORTEN_TOKEN_FILE --output-file=credentials.json
gcloud auth login --cred-file=credentials.json
Authenticated with external account credentials for: [skyportenstorageconsumer@external-test-foo-333333.iam.gserviceaccount.com].
Your current project is [external-test-foo-333333]

gcloud storage ls gs://$BUCKET 
gs://[bucket name]/foo_remote.txt

gcloud storage cp gs://$BUCKET/foo_remote.txt foo_local.txt 
Copying gs://[bucket name]/foo_remote.txt to file://foo_local.txt
  Completed files 1/1 | 4.0B/4.0B    

```