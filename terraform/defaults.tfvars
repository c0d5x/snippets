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
