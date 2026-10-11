"""CON-66 engine-timeout proof stack.

One tf_executor order whose execgroup applies a 400 s time_sleep. The config
sets ``timeout`` (T, default 120) so the apply outlives T on the engine's
Lambda target. No AWS resource is created.

Also used by ``codebuild-compute/`` (CON-77): at ``timeout`` 900 the order runs
on CodeBuild, and the ``compute_type`` argument the TFConstructor helper
declares rides to the build as its compute size. This version locks the
``tf_executor`` that declares ``compute_type``.
"""

from config0_publisher.terraform import TFConstructor


def run(stackargs):
    stack = newStack(stackargs)

    stack.parse.add_required(key="sleep_name",
                             types="str")

    # the order's timeout T; the config sets it, nothing in this stack clobbers it
    stack.parse.add_optional(key="timeout",
                             default=120,
                             types="int")

    stack.parse.add_optional(key="aws_default_region",
                             default="ap-northeast-1",
                             tags="tfvar,db,resource,tf_exec_env",
                             types="str")

    stack.add_execgroup("williaumwu:::config0_yamls_repos::engine_timeout",
                        "tf_execgroup")

    stack.add_substack("config0-hub:::config0_core::tf_executor")

    stack.init_variables()
    stack.init_execgroups()
    stack.init_substacks()

    tf = TFConstructor(stack=stack,
                       execgroup_name=stack.tf_execgroup.name,
                       provider="aws",
                       tf_runtime="tofu:1.10.6",
                       resource_name=stack.sleep_name,
                       resource_type="time_sleep")

    tf.include(values={
        "aws_default_region": stack.aws_default_region,
        "name": stack.sleep_name
    })

    stack.tf_executor.insert(display=True,
                             **tf.get())

    return stack.get_results()
