### Config for vRA Provider -  Auth/Cloud Accounts
variable "url" {
}
variable "refresh_token" {
}
### Config for vRA Provider - Cloud Zone
#variable "cloud_account" {
#}
#variable "region_1" {
#}

#variable "region_2" {
#}

variable "zones" {
  type    = list(string)
  default = ["us-west-1a"]
}


variable "project_name" {

}

variable "project_desc" {

}


