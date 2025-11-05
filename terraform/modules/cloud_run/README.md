# Cloud Run module

This module deploys a single Cloud Run service and configures an invoker IAM binding.

Inputs
- `name` (string) - service name
- `location` (string) - region (eg. `us-central1`)
- `image` (string) - container image
- `port` (number) - container port
- `env` (map(string)) - environment variables
- `traffic_percent` (number) - traffic percent for latest revision
- `public` (bool) - if true, grants `allUsers` the `roles/run.invoker` role
- `invoker_members` (list(string)) - alternative members when `public = false`

Outputs
- `service_name`
- `service_url`
