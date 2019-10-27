### Config for vRA Provider -  Auth/Cloud Accounts
variable "url" {
}
variable "refresh_token" {
}


variable "zones" {
  type    = list(string)
  default = ["us-west-1a"]
}


variable "project_name" {

}

variable "project_desc" {
}

variable "project_admins" {
}

variable "project_members" {
}


