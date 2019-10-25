#### VRA Provider - Cloud Account
provider "vra" {
  url           = var.url
  refresh_token = var.refresh_token


data "vra_zone" "this" {
  count = length(var.zones)
  name          = var.zones[count.index]
}

### Projects
resource "vra_project" "this" {
  name        = var.project_name
  description = var.project_desc

  
  dynamic zone_assignments {
    for_each = data.vra_zone.this
    content {
      zone_id       = "${zone_assignments.value.id}"
      priority      = 1
      max_instances = 0
      }

    }

}


