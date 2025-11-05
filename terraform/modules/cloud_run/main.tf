resource "google_cloud_run_service" "this" {
  name     = var.name
  location = var.location

  template {
    spec {
      containers {
        image = var.image

        ports {
          container_port = var.port
        }

        dynamic "env" {
          for_each = var.env
          content {
            name  = env.key
            value = env.value
          }
        }
      }
    }
  }

  traffic {
    percent         = var.traffic_percent
    latest_revision = true
  }
}

resource "google_cloud_run_service_iam_binding" "invoker" {
  location = google_cloud_run_service.this.location
  service  = google_cloud_run_service.this.name
  role     = "roles/run.invoker"

  members = var.public ? ["allUsers"] : var.invoker_members
}
