#### VRA Provider - Cloud Account
provider "vra" {
  url           = var.url
  refresh_token = var.refresh_token
}

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

data "vra_zone" "zoneAPSE1" {
  name = var.zone_apse1
}

data "vra_zone" "zoneAPSE2" {
  name = var.zone_apse2
}

### Projects

resource "vra_project" "this" {
  name        = var.project_name
  description = var.project_desc

  zone_assignments {
    zone_id       = "${vra_zone.zoneAPSE1.id}"
    priority      = 1
    max_instances = 0
  }

   zone_assignments {
    zone_id       = "${data.vra_zone.zoneAPSE2.id}"
    priority      = 1
    max_instances = 0
  }
}


