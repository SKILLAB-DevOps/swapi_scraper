variable "name" {
  type        = string
  description = "Cloud Run service name"
}

variable "location" {
  type        = string
  description = "GCP region for Cloud Run"
}

variable "image" {
  type        = string
  description = "Container image to deploy"
}

variable "port" {
  type        = number
  default     = 8080
  description = "Container port"
}

variable "env" {
  type        = map(string)
  default     = {}
  description = "Environment variables to set on the container"
}

variable "traffic_percent" {
  type    = number
  default = 100
}

variable "public" {
  type        = bool
  default     = true
  description = "Whether the service should be publicly invokable (allUsers)"
}

variable "invoker_members" {
  type        = list(string)
  default     = []
  description = "List of IAM members to grant run.invoker to when public = false"
}
