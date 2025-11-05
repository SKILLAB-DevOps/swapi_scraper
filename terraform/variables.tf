variable "project_id" {
  type        = string
  default     = ""
  description = "GCP Project id, put your own project id here"
}

variable "db_instance_name" {
  type        = string
  default     = "swapi-test"
  description = "db name"
}

variable "database_name" {
  type        = string
  default     = "swapi-test"
  description = "db name"
}

variable "database_user_name" {
  type        = string
  default     = "swapi-user"
  description = "db user name"
}

variable "database_user_pass" {
  type        = string
  default     = "f0(,,~~?6%S~SRp="
  description = "db user pass"
  sensitive   = true
}