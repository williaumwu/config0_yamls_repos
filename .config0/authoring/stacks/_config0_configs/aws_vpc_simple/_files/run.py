"""
# Copyright (C) 2025 Gary Leong <gary@config0.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from config0_publisher.terraform import TFConstructor


def run(stackargs):

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_required(key="vpc_name",
                             tags="tfvar,db",
                             types="str")

    stack.parse.add_optional(key="tier_level",
                             types="str,int")

    # vpc_id is only used for "selectors"
    # e.g. you need to create the vpc before getting the id unless
    # using a selector to query the value after creation
    stack.parse.add_optional(key="vpc_id",
                             types="str",
                             default="null")

    # if eks_cluster is specified, then add the correct tags to the vpc
    stack.parse.add_optional(key="eks_cluster",
                             types="str")

    # opt-in SSM interface endpoints (ssm/ssmmessages/ec2messages) for
    # no-public-IP SSM-managed hosts; default false leaves existing
    # consumers unchanged
    # we need to use string value for false b/c tfvar
    stack.parse.add_optional(key="enable_ssm_endpoints",
                             default="false",
                             tags="tfvar",
                             types="bool")

    # opt-in NAT gateway - NAT only where the user package needs public
    # package repositories; default false leaves existing consumers unchanged
    # we need to use string value for false b/c tfvar
    stack.parse.add_optional(key="enable_nat_gateway",
                             default="false",
                             tags="tfvar",
                             types="bool")

    # docker image to execute terraform with
    stack.parse.add_optional(key="aws_default_region",
                             default="eu-west-1",
                             tags="tfvar,db,resource,tf_exec_env",
                             types="str")

    # Add execgroup
    stack.add_execgroup("config0-hub:::aws_networking::vpc_simple",
                        "tf_execgroup")

    # Add substack
    stack.add_substack('config0-hub:::config0_core::tf_executor')
    stack.add_substack('config0-hub:::aws_networking::aws_sg')

    # Initialize
    stack.init_variables()
    stack.init_execgroups()
    stack.init_substacks()

    # set variables
    _default_tags = {"vpc_name": stack.vpc_name}

    vpc_tags = _default_tags.copy()
    public_subnet_tags = _default_tags.copy()
    private_subnet_tags = _default_tags.copy()

    # if eks_cluster is provided, we modify the configs
    # if we are using a vpc without a nat, the eks must be in public network
    # the internal lb must also be in public
    if stack.get_attr("eks_cluster"):
        vpc_tags[f"kubernetes.io/cluster/{stack.eks_cluster}"] = "shared"
        public_subnet_tags["kubernetes.io/role/elb"] = "1"
        private_subnet_tags["kubernetes.io/role/internal_elb"] = "1"

    stack.set_variable("vpc_tags",
                       vpc_tags,
                       tags="tfvar",
                       types="dict")

    stack.set_variable("public_subnet_tags",
                       public_subnet_tags,
                       tags="tfvar",
                       types="dict")

    stack.set_variable("private_subnet_tags",
                       private_subnet_tags,
                       tags="tfvar",
                       types="dict")

    stack.set_variable("timeout", 600)

    # use the terraform constructor (helper)
    tf = TFConstructor(stack=stack,
                       execgroup_name=stack.tf_execgroup.name,
                       provider="aws",
                       tf_runtime="tofu:1.10.6",
                       resource_name=stack.vpc_name,
                       resource_type="vpc")

    tf.include(values={
        "aws_default_region": stack.aws_default_region,
        "name": stack.vpc_name,
        "vpc": stack.vpc_name,
        "vpc_name": stack.vpc_name
    })

    # Stamp region label so selector match.keys.region resolves this resource.
    # The canonical key is "region" (the short form used by selectors); the stack
    # input arrives as "aws_default_region" — normalize here, authoring-side, so
    # config0_publisher stays provider-agnostic.
    tf.include(values={
        "labels": {
            "region": stack.aws_default_region,
            "provider": "aws",
        }
    })

    # publish the info
    tf.output(keys=["aws_default_region",
                    "vpc_name",
                    "vpc_id"])

    # finalize the tf_executor
    stack.tf_executor.insert(display=True,
                             **tf.get())

    ##################################
    # add security groups
    ##################################
    arguments = {"vpc_name": stack.vpc_name,
                 "aws_default_region": stack.aws_default_region}

    if stack.get_attr("vpc_id"):
        arguments["vpc_id"] = stack.vpc_id

    if stack.get_attr("cloud_tags_hash"):
        arguments["cloud_tags_hash"] = stack.cloud_tags_hash

    if stack.get_attr("tier_level"):
        arguments["tier_level"] = stack.tier_level

    inputargs = {
        "arguments": arguments,
        "automation_phase": "infrastructure",
        "human_description": f'Creating security groups for VPC {stack.vpc_name}'
    }

    stack.aws_sg.insert(display=True, **inputargs)

    return stack.get_results()
