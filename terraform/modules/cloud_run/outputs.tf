output "service_name" {
  value = google_cloud_run_service.this.name
}

output "service_url" {
  value = try(google_cloud_run_service.this.status[0].url, "")
}
