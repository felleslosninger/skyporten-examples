# Bruk av Azure Service Principal med Federated Identity basert på Maskinporten

## Hva du trenger for å komme i gang

Du må ha en Azure konto, og az CLI-verktøy installert.


## Login i Azure

Login i Azure fra kommandolinjen:

```
az login
{
...
    "tenantId": "5e55abcd-dddd-4444-bbbb-4a4a4a4a4a4aa",
...
}
# Used later for logging in with Skyporten OIDC token
export AZURE_TENANT_ID="5e55abcd-dddd-4444-bbbb-4a4a4a4a4a4aa"
```

## Define SUBSCRIPTION_ID

Find the value of the subscription you want to work in and create objects in.

List subscriptions:

``````bash
az account subscription list

# Find the subscription id of the subscription you want to use
az account subscription list
[
  {
...
    "displayName": "skyportentest",
    "id": "/subscriptions/77777777-7777-7777-7777-777777777777",
    "state": "Enabled",
    "subscriptionId": "77777777-7777-7777-7777-777777777777",
...
  }
]
```

Export the subscription id:

``````bash
export SUBSCRIPTION_ID="77777777-7777-7777-7777-777777777777"
``````

### Add federated credentials

#### Create credential.json

credential.json should contain this:

``````json
{
    "name": "oidcpilotcreds",
    "issuer": "https://sky.maskinporten.dev/",
    "subject": "0192:999999999",
    "description": "Testing skyporten",
    "audiences": [
        "https://sky.organisasjonsnavn.no"
    ]
}
``````

## Create a resource group, storage account and storage share

``````bash
export STORAGE_ACC="skyportenstoragepilot"

export STORAGE_RG="filestorage-rg"
export IDENTITY="SkyvesenetIdentity"

az group create --name $STORAGE_RG --location northeurope

export STORAGE_ACC="skyportenstoragepilot"
az storage account create --name $STORAGE_ACC --resource-group $STORAGE_RG --location northeurope  --sku Standard_RAGRS --kind StorageV2
{
...
  "id": "/subscriptions/11111111-a899-447c-b453-111111111111/resourceGroups/filestorage-rg/providers/Microsoft.Storage/storageAccounts/skyportenstoragepilot",
...
}

export FILE_STORAGE_ID="/subscriptions/11111111-a899-447c-b453-111111111111/resourceGroups/filestorage-rg/providers/Microsoft.Storage/storageAccounts/skyportenstoragepilot"

export STORAGE_SHARE="skyporten-share"
az storage share create --account-name $STORAGE_ACC --name $STORAGE_SHARE
``````

## Create a managed identity

The identity will be used to give access to the storage share

``````bash
az identity create --name "$IDENTITY" --resource-group "$STORAGE_RG"
Resource provider 'Microsoft.ManagedIdentity' used by this operation is not registered. We are registering for you.
Registration succeeded.
{
  "clientId": "44444444-cf66-4934-b34c-444444444444",
  "id": "/subscriptions/11111111-a899-447c-b453-111111111111/resourcegroups/filestorage-rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/SkyvesenetIdentity",
  "location": "northeurope",
  "name": "SkyvesenetIdentity",
  "principalId": "22222222-f9fb-4b76-a853-222222222222",
  "resourceGroup": "filestorage-rg",
  "systemData": null,
  "tags": {},
  "tenantId": "33333333-d105-4b01-aa7c-333333333333",
  "type": "Microsoft.ManagedIdentity/userAssignedIdentities"
}

export SERVICE_PRINCIPAL_ID="22222222-f9fb-4b76-a853-222222222222"
export IDENTITY_CLIENT_ID="44444444-cf66-4934-b34c-444444444444"
``````

## Create federated credential

``````bash
export CREDENTIAL_NAME="SkyvesenetFedCreds"

az identity federated-credential create --name "$CREDENTIAL_NAME" --identity-name "$IDENTITY" --resource-group "$STORAGE_RG" --issuer "https://sky.maskinporten.dev/" --subject "0192:917422575" --audiences "https://sky.organisasjonsnavn.no"
{
  "audiences": [
    "https://sky.menneskemaskin.no"
  ],
  "id": "/subscriptions/11111111-a899-447c-b453-111111111111/resourcegroups/filestorage-rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/SkyvesenetIdentity/federatedIdentityCredentials/SkyvesenetFedCreds",
  "issuer": "https://sky.maskinporten.dev/",
  "name": "SkyvesenetFedCreds",
  "resourceGroup": "filestorage-rg",
  "subject": "0192:917422575",
  "systemData": null,
  "type": "Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials"
}
``````

## Assign roles to the managed identity

``````bash
az role assignment create --role contributor \
  --subscription $SUBSCRIPTION_ID \
  --assignee-object-id $SERVICE_PRINCIPAL_ID \
  --assignee-principal-type ServicePrincipal \
  --scope "$FILE_STORAGE_ID"

# Federated identities also need "Storage File Data Privileged..." roles

az role assignment create --assignee "$SERVICE_PRINCIPAL_ID" \
  --role "Storage File Data Privileged Contributor" \
  --scope "$FILE_STORAGE_ID"

``````

## Upload a file to the storage

``````bash
echo foo > ./bar.txt

# Upload the file
az storage file upload --account-name $STORAGE_ACC --share-name $STORAGE_SHARE --path remotebar.txt --source ./bar.txt
``````

## Logout

``````bash
```
# Contributor role for the service principal
az role assignment create --role contributor --subscription $SUBSCRIPTION_ID --assignee-object-id $SERVICE_PRINCIPAL_ID --assignee-principal-type ServicePrincipal --scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$STORAGE_RG

# Blob access
az role assignment create --assignee "$SERVICE_PRINCIPAL_ID" \
  --role "Storage Blob Data Contributor" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$STORAGE_RG/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACC"

# Federated identities also need "Storage File Data Privileged..." roles
az role assignment create --assignee "$SERVICE_PRINCIPAL_ID" \
  --role "Storage File Data Privileged Reader" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$STORAGE_RG/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACC"
  
# Reader might be enough, but I added this one too
az role assignment create --assignee "$SERVICE_PRINCIPAL_ID" \
  --role "Storage File Data Privileged Contributor" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$STORAGE_RG/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACC"

```

## 7. Log in with Maskinporten credentials and download a file

```
# Logout from regular azure developer session, if active
az logout
``````

## Generate a skyporten token

See [token instructions](/token.md) on how to generate a token.

``````bash
# Copy the token value and export it, to use it to log in
export SKYPORTEN_TOKEN="aaaaa....bbbbbb"
``````

The unpacked token will look something like this:

``````json
{
  "aud": "https://entur.org",
  "sub": "0192:917422575",
  "scope": "entur:foo.1",
  "iss": "https://sky.maskinporten.dev/",
  "client_amr": "private_key_jwt",
  "token_type": "Bearer",
  "exp": 1694222211,
  "iat": 1694333311,
  "client_id": "abcd1234-1234-abcd-abcd-12341234abcd",
  "jti": "lwlwlwlw4lwlwlwlwl4lwlw4-lw-lwl4lwl4lwl4lwl4",
  "consumer": {
    "authority": "iso6523-actorid-upis",
    "ID": "0192:917422575"
  }
}
``````

## Login with the federated credentials and download a file, to test access

``````bash
# Login with skyporten token
az login --service-principal -u $IDENTITY_CLIENT_ID -t $AZURE_TENANT_ID --federated-token $SKYPORTEN_TOKEN

# List files
az storage file list --account-name $STORAGE_ACC --share-name $STORAGE_SHARE | jq .[0].name

# Download a file
az storage file download --account-name $STORAGE_ACC --share-name $STORAGE_SHARE --auth-mode login --enable-file-backup-request-intent --path remotebar.txt
``````


## Troubleshooting

### Missing trailing slash (`/`) in issue argument when calling `az identity federated-credential create`

``````bash
az login --service-principal -u $IDENTITY_CLIENT_ID -t $AZURE_TENANT_ID --federated-token $SKYPORTEN_TOKEN
AADSTS70021: No matching federated identity record found for presented assertion. Assertion Issuer: 'https://sky.maskinporten.dev/'. Assertion Subject: '0192:917422575'. Assertion Audience: 'https://sky.foo.com'.
``````

The issuer must exactly match the issuer in the credential. Update or recreate the credential with trailing slash in the issuer.


### Token timeout error (as expected since token has timed out)

``````bash
az login --service-principal -u $IDENTITY_CLIENT_ID -t $AZURE_TENANT_ID --federated-token $SKYPORTEN_TOKEN
AADSTS700024: Client assertion is not within its valid time range. Current time: 2023-08-01T11:08:01.5274809Z, assertion valid from 2023-08-01T09:28:26.0000000Z, expiry time of assertion 2023-08-01T10:28:26.0000000Z. Review the documentation at https://docs.microsoft.com/azure/active-directory/develop/active-directory-certificate-credentials .
``````

### Wrongly using service principal id instead of client id

``````bash
az login --service-principal -u $SERVICE_PRINCIPAL_ID -t $AZURE_TENANT_ID --federated-token $SKYPORTEN_TOKEN
AADSTS700016: Application with identifier '22222222-f9fb-4b76-a853-222222222222' was not found in the directory 'Default Directory'. This can happen if the application has not been installed by the administrator of the tenant or consented to by any user in the tenant. You may have sent your authentication request to the wrong tenant.
``````

Use IDENTITY_CLIENT_ID instead.

