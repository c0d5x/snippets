
variable "region" {
    default = "us-west-1"
}

variable "azs" {
    default = ["us-west-1b", "us-west-1c"]
}

variable "instance_type" {
    default = "t2.micro"
}

variable "ami" {
    default = "ami-14fcaf74"
}

variable "keyname" {
    default = "gl-josehidalgo-pub-ssh"
}

variable "securitygroups" {
    default = "pocdeploy"
}

variable "placement" {
    default ="default"
}


provider "aws" {
    region = "${var.region}"
}


resource "aws_elb" "elbpocdeploy" {
  name = "elbpocdeploy"
  availability_zones = "${var.azs}"

  listener {
    instance_port = 8080
    instance_protocol = "http"
    lb_port = 80
    lb_protocol = "http"
  }

  health_check {
    healthy_threshold = 2
    unhealthy_threshold = 2
    timeout = 3
    target = "HTTP:8080/"
    interval = 30
  }

  cross_zone_load_balancing = true
  idle_timeout = 400
  connection_draining = true
  connection_draining_timeout = 400
}

resource "aws_launch_configuration" "lcpocdeploy" {
    name_prefix = "lcpocdeploy"
    image_id = "${var.ami}"
    instance_type = "${var.instance_type}"
    key_name = "${var.keyname}"
    security_groups = ["${var.securitygroups}"]
    placement_tenancy = "${var.placement}"
    lifecycle {
      create_before_destroy = true
    }
}


resource "aws_autoscaling_group" "asgpocdeploy" {
    name = "asgpocdeploy"
    launch_configuration = "${aws_launch_configuration.lcpocdeploy.name}"
    load_balancers = ["${aws_elb.elbpocdeploy.name}"]
    lifecycle {
      create_before_destroy = true
    }
    min_size = 1
    max_size = 3
    desired_capacity = 2
    availability_zones = "${var.azs}"
}
