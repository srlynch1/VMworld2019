module "vra" {
  source  = "app.terraform.io/vmworld/vra/provider"
  version = "0.1.3"
}

#### VRA Provider - API and Token
provider "vra" {
  url           = var.url
  refresh_token = var.refresh_token
}

#lookup each Cloud zone by name 
data "vra_zone" "this" {
  count = length(var.zones)
  name          = var.zones[count.index]
}

### Projects
resource "vra_project" "this" {
  name        = var.project_name
  description = var.project_desc
  administrators = var.project_admins
  members = var.project_members

  #assign each zone to the project
  dynamic zone_assignments {
    for_each = data.vra_zone.this
    content {
      zone_id       = "${zone_assignments.value.id}"
      priority      = 1
      max_instances = 0
      }

    }

}


