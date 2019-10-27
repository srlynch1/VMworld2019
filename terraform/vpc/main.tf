#Configure the AWS provider
provider "aws" {
  version = "~> 2.18"
  region = "${var.vpc_region}"
  access_key = "${var.aws_access_key_id}"
  secret_key = "${var.aws_secret_access_key}"
}

# Define a vpc
resource "aws_vpc" "vpc_name" {
  cidr_block = var.vpc_cidr_block
  tags = {
    Name = "${var.vpc_name}"
  }
}

# Internet gateway for the public subnet
resource "aws_internet_gateway" "dev_ig" {
  vpc_id = "${aws_vpc.vpc_name.id}"
  tags = {
    Name = "operationsaasgateway"
  }
}

# Public subnet
resource "aws_subnet" "vpc_public_sn" {
  vpc_id = "${aws_vpc.vpc_name.id}"
  cidr_block = "${var.vpc_public_subnet_cidr}"
  #availability_zone = "${lookup(var.availability_zone, var.vpc_region)}"
  tags = {
    Name = "OperationsaasPublicSubnet"
  }
}

# Private subnet
resource "aws_subnet" "vpc_private_sn" {
  vpc_id = "${aws_vpc.vpc_name.id}"
  cidr_block = "${var.vpc_private_subnet_cidr}"
  #availability_zone = "${vpc_region}
  tags = {
    Name = "OperationsaasPrivateSubnet"
  }
}

# Routing table for public subnet
resource "aws_route_table" "vpc_public_sn_rt" {
  vpc_id = "${aws_vpc.vpc_name.id}"
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = "${aws_internet_gateway.dev_ig.id}"
  }
  tags = {
    Name = "operationsaasrt"
  }
}

# Associate the routing table to public subnet
resource "aws_route_table_association" "vpc_public_sn_rt_assn" {
  subnet_id = "${aws_subnet.vpc_public_sn.id}"
  route_table_id = "${aws_route_table.vpc_public_sn_rt.id}"
}

# Security group
resource "aws_security_group" "vpc_public_sg" {
  name = "dev_pubic_sg"
  description = "dev public access security group"
  vpc_id = "${aws_vpc.vpc_name.id}"

  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = [
      "${var.vpc_access_from_ip_range}"]
  }

  ingress {
    from_port = 0
    to_port = 0
    protocol = "tcp"
    cidr_blocks = [
      "${var.vpc_public_subnet_cidr}"]
  }

  egress {
    # allow all traffic to private SN
    from_port = "0"
    to_port = "0"
    protocol = "-1"
    cidr_blocks = [
      "0.0.0.0/0"]
  }
  tags = {
    Name = "operationsaaseg"
  }
}

resource "aws_security_group" "vpc_private_sg" {
  name = "dev_private_sg"
  description = "dev security group to access private ports"
  vpc_id = "${aws_vpc.vpc_name.id}"

  # allow memcached port within VPC
  ingress {
    from_port = 11211
    to_port = 11211
    protocol = "tcp"
    cidr_blocks = [
      "${var.vpc_public_subnet_cidr}"]
  }

  

  # allow mysql port within VPC
  ingress {
    from_port = 3306
    to_port = 3306
    protocol = "tcp"
    cidr_blocks = [
      "${var.vpc_public_subnet_cidr}"]
  }

  egress {
    from_port = "0"
    to_port = "0"
    protocol = "-1"
    cidr_blocks = [
      "0.0.0.0/0"]
  }
  tags = {
    Name = "operationsaaseg"
  }
}

output "vpc_region" {
  value = var.vpc_region
}

output "vpc_id" {
  value = "${aws_vpc.vpc_name.id}"
}

output "vpc_public_sn_id" {
  value = "${aws_subnet.vpc_public_sn.id}"
}

output "vpc_private_sn_id" {
  value = "${aws_subnet.vpc_private_sn.id}"
}

output "vpc_public_sg_id" {
  value = "${aws_security_group.vpc_public_sg.id}"
}

output "vpc_private_sg_id" {
  value = "${aws_security_group.vpc_private_sg.id}"
}

/*
#### VRA Provider - Cloud Account
provider "vra" {
  url           = var.url
  refresh_token = var.refresh_token
}


resource "vra_cloud_account_aws" "this" {
  name        = "tf-vra-cloud-account-aws"
  description = "terraform test cloud account aws"
  access_key  = var.aws_access_key_id
  secret_key  = var.aws_secret_access_key
  regions     = [var.region_1, var.region_2]

  tags {
    key   = "foo"
    value = "bar"
  }
}

data "vra_region" "region_1" {
  cloud_account_id = vra_cloud_account_aws.this.id
  region           = var.region_1
}

data "vra_region" "region_2" {
  cloud_account_id = vra_cloud_account_aws.this.id
  region           = var.region_2
}
*/

### Cloud Zones

/*

data "vra_cloud_account_aws" "this" {
  name = var.cloud_account
  depends_on = [vra_cloud_account_aws.this]
}

data "vra_region" "APSE1" {
  cloud_account_id = data.vra_cloud_account_aws.this.id
  region           = var.region_1
}

resource "vra_zone" "zoneAPSE1" {
  name        = "ANZ AWS APSE1 TF"
  description = "AWS ap-southeast-1 (Singapore)"
  region_id   = data.vra_region.APSE1.id

  tags {
    key   = "tf-platform"
    value = ":aws"
  }

  tags {
    key   = "tf-region"
    value = "singapore"
  }
}

data "vra_region" "APSE2" {
  cloud_account_id = data.vra_cloud_account_aws.this.id
  region           = var.region_2
}

resource "vra_zone" "zoneAPSE2" {
  name        = "ANZ AWS APSE2 TF"
  description = "AWS ap-southeast-2 (Sydney)"
  region_id   = data.vra_region.APSE2.id

  tags {
    key   = "tf-platform"
    value = "aws"
  }

  tags {
    key   = "tf-region"
    value = "sydney"
  }
}

### Network Profiles

data "vra_fabric_network" "subnet_1" {
  filter = "name eq 'OperationsaasPrivateSubnet' and cloudAccountId eq '${vra_cloud_account_aws.this.id}'"
  depends_on = [vra_zone.zoneAPSE2]
}

data "vra_fabric_network" "subnet_2" {
  filter = "name eq 'OperationsaasPublicSubnet' and cloudAccountId eq '${vra_cloud_account_aws.this.id}'"
  depends_on = [vra_zone.zoneAPSE2]
}

resource "vra_network_profile" "simple" {
  name        = "np-aws"
  description = "AWS Network Profiles"
  region_id   = data.vra_region.APSE2.id

  fabric_network_ids = [
    data.vra_fabric_network.subnet_1.id,
    data.vra_fabric_network.subnet_2.id
  ]

  isolation_type = "NONE"

  tags {
    key   = "foo"
    value = "bar"
  }
}

*/

### Network



