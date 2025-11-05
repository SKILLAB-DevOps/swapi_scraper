variable "instance_name" {
  type        = string
  description = "DB Instance name in GCP"
}

variable "database_name" {
  type        = string
  description = "DB Name for connection"
}

variable "database_username" {
  type        = string
  description = "db username"
}

variable "database_password" {
  type        = string
  description = "password"
}
