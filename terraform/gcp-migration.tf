# Terraform Cloud managed deployment
# Target Infrastructure: GCP


provider "google" {
  project = var.gcp_project_id
  region  = "us-central1"
}

resource "google_bigquery_dataset" "inventory_analytics" {
  dataset_id    = "inventory_analytics_prod"
  friendly_name = "Inventory Analytics Production"
  location      = "US"
}

resource "google_bigquery_table" "inventory_master" {
  dataset_id = google_bigquery_dataset.inventory_analytics.dataset_id
  table_id   = "inventory_master"

  schema = file("${path.module}/../schemas/inventory_master.json")
}

# Operational queries: Cloud SQL
resource "google_sql_database_instance" "inventory_operational" {
  name             = "inventory-ops-instance"
  database_version = "POSTGRES_13"
  region           = "us-central1"

  settings {
    tier = "db-f1-micro"
    backup_configuration {
      enabled = true
      point_in_time_recovery_enabled = true
    }
  }
}
