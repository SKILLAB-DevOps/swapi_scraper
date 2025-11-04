provider "google" {
  project     = "" # put your own project id here
  region      = "us-central1"
  zone        = "us-central1-a"
}

resource "google_sql_database_instance" "swapi_db" {
  name             = var.db_instance_name
  database_version = "POSTGRES_16"
  region           = "us-central1"

  settings {
    tier    = "db-perf-optimized-N-2"
    edition = "ENTERPRISE_PLUS"

    ip_configuration {
      authorized_networks {
        name = "internet"
        value = "0.0.0.0/1"
      }
    }

  }
}

resource "google_sql_database" "database" {
  name     = var.database_name
  instance = google_sql_database_instance.swapi_db.name
}

resource "google_sql_user" "users" {
  name     = var.database_user_name
  instance = google_sql_database_instance.swapi_db.name
  password = var.database_user_pass
}

resource "google_cloud_run_service" "default" {
  name     = "swapi-app"
  location = "us-central1"

  template {
    spec {
      containers {
        image = "us-central1-docker.pkg.dev/effective-relic-473715-j8/swapi-scraper/swapi:0.0.1"
        env {
          name = "DATABASE_URL"
          value = "postgresql://${var.database_user_name}:${var.database_user_pass}@${google_sql_database_instance.swapi_db.ip_address.0.ip_address}:5432/${var.database_name}"
          
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}