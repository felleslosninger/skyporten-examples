resource "google_iam_workload_identity_pool" "maskinporten_test" {
  workload_identity_pool_id = "test-maskinporten"
  display_name              = "TEST Maskinporten"
  description               = "Maskinporten sitt testmiljø"
} 

resource "google_iam_workload_identity_pool_provider" "maskinporten" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.maskinporten_test.workload_identity_pool_id
  workload_identity_pool_provider_id = "test-maskinporten"
  attribute_mapping                  = {
          "attribute.maskinportenscope" = "assertion.scope"
          "google.subject"              = "assertion.consumer.ID"
          "attribute.clientaccess"      = "\"client::\" + assertion.consumer.ID + \"::\" + assertion.scope"
        }
  display_name                       = "Test Maskinporten Provider"
  description                        = "OIDC identity pool provider for Maskinporten"
  oidc {
    allowed_audiences = ["https://entur.org",
              "https://hoc-cluster-public-vault-e58f231b.dada9b17.z1.hashicorp.cloud"]
    issuer_uri        = "https://sky.maskinporten.dev/"
  }

}

output "pool_provider_id" {
  value = google_iam_workload_identity_pool_provider.maskinporten.id
}
