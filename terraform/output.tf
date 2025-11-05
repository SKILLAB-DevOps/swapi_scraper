output "cloud_run_service_url" {
  description = "URL for the deployed Cloud Run service"
  value       = module.cloud_run.service_url
}

output "cloud_run_service_name" {
  description = "Cloud Run service name"
  value       = module.cloud_run.service_name
}
