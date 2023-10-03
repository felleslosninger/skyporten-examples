resource "google_service_account" "consumer_scope_user" {
  account_id   = "maskinporten-917422575-skyss-1"
  description = "Example service account for scope entur:skyss.1 for orgno 917422575"
}

data "google_iam_policy" "clientaccess" {
  binding {
    role = "roles/iam.workloadIdentityUser"

    members = [
      "principalSet://iam.googleapis.com/projects/207740593944/locations/global/workloadIdentityPools/test-maskinporten/attribute.clientaccess/client::0192:917422575::entur:skyss.1",
    ]
  }
}

resource "google_service_account_iam_policy" "foo" {
  service_account_id = google_service_account.consumer_scope_user.name
  policy_data        = data.google_iam_policy.clientaccess.policy_data
}

#https://github.com/hashicorp/terraform-provider-google/issues/12446