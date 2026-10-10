"""CodeBuild fail-fast integration stack.

One tf_executor order whose execgroup fails at ``plan`` on a precondition
that is always false. The config sets ``timeout`` (T, default 900): above 800
the publisher routes the order to the engine's CodeBuild target, so this
proves a CodeBuild build that dies in its first seconds fails the order
within about a minute, and that each retry is a real build. No AWS resource
is created.
"""

from config0_publisher.terraform import TFConstructor


def run(stackargs):
    stack = newStack(stackargs)

    stack.parse.add_required(key="failfast_name",
                             types="str")

    # the order's timeout T; above 800 the publisher picks CodeBuild
    stack.parse.add_optional(key="timeout",
                             default=900,
                             types="int")

    stack.parse.add_optional(key="aws_default_region",
                             default="ap-northeast-1",
                             tags="tfvar,db,resource,tf_exec_env",
                             types="str")

    stack.add_execgroup("williaumwu:::config0_yamls_repos::codebuild_failfast",
                        "tf_execgroup")

    stack.add_substack("config0-hub:::config0_core::tf_executor")

    stack.init_variables()
    stack.init_execgroups()
    stack.init_substacks()

    tf = TFConstructor(stack=stack,
                       execgroup_name=stack.tf_execgroup.name,
                       provider="aws",
                       tf_runtime="tofu:1.10.6",
                       resource_name=stack.failfast_name,
                       resource_type="terraform_data")

    tf.include(values={
        "aws_default_region": stack.aws_default_region,
        "name": stack.failfast_name
    })

    stack.tf_executor.insert(display=True,
                             **tf.get())

    return stack.get_results()
