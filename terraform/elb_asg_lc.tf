
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

  tags {
    Name = "pocdeploy"
  }
}

resource "aws_launch_configuration" "lcpocdeploy" {
    name = "lcpocdeploy"
    image_id = "${var.ami}"
    instance_type = "${var.instance_type}"
    key_name = "${var.keyname}"
    security_groups = "${securitygroups}"
    placement_tenancy = "${placement}"
    tags {
      Name = "pocdeploy"
    }
}


resource "aws_autoscaling_group" "asgpocdeploy" {
    name = "asgpocdeploy"
    launch_configuration = "${aws_launch_configuration.lcpocdeploy.name}"
    load_balancers = ["${aws_elb.elbpocdeploy.name}"]
    lifecycle {
      create_before_destroy = true
    }
    availability_zones = "${azs}"
    tags {
      Name = "pocdeploy"
    }
}
