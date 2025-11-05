provider "google" {
  project = var.project_id
  region  = "us-central1"
  zone    = "us-central1-a"
}

terraform {
  backend "gcs" {
    bucket = "tfstate-473715"
    prefix = "terraform/state"
  }
}

module "db" {
  source = "./modules/db"

  instance_name = var.db_instance_name
  database_name = var.database_name
  database_username = var.database_user_name
  database_password = var.database_user_pass
}

module "cloud_run" {
  source = "./modules/cloud_run"

  name     = "swapi-app"
  location = "us-central1"
  image    = "us-central1-docker.pkg.dev/effective-relic-473715-j8/swapi-scraper/swapi:0.0.1"
  port     = 8000

  env = {
    DATABASE_URL = "postgresql://${var.database_user_name}:${var.database_user_pass}@${module.db.ip_address}:5432/${var.database_name}"
  }

  traffic_percent = 100
  public          = true
  invoker_members = []
}