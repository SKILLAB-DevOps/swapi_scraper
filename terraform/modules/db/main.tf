resource "google_sql_database_instance" "this" {
  name             = var.instance_name
  database_version = "POSTGRES_16"
  region           = "us-central1"
  deletion_protection = false

  settings {
    tier    = "db-perf-optimized-N-2"
    edition = "ENTERPRISE_PLUS"

    ip_configuration {
      authorized_networks {
        name  = "internet"
        value = "0.0.0.0/1"
      }
    }

  }
}

resource "google_sql_database" "database" {
  name     = var.database_name
  instance = google_sql_database_instance.this.name
}

resource "google_sql_user" "users" {
  instance = google_sql_database_instance.this.name
  name     = var.database_username
  password = var.database_password
}