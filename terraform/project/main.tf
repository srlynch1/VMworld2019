#### VRA Provider - Cloud Account
provider "vra" {
  url           = var.url
  refresh_token = var.refresh_token
}

/*
data "vra_cloud_account_aws" "this" {
  name = var.cloud_account
}

data "vra_region" "regionAPSE2" {
  cloud_account_id = data.vra_cloud_account_aws.this.id
  region = "ap-southeast-2"
}

data "vra_region" "regionAPSE1" {
  cloud_account_id = data.vra_cloud_account_aws.this.id
  region = "ap-southeast-1"
}

*/

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


