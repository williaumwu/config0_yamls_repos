"""Test stack for CON-131 phase 4 acceptance, step 5: an ai workflow stack whose
run_timeout is its declared default when config0.yaml omits it. It runs one
empty_stack order and nothing else (no server, no model call). The acceptance reads
the frozen run_timeout on the hub row and the QHost run row, then changes this
default, rescans, reruns, and checks the frozen value did not change.
"""


def run(stackargs):

    stack = newStack(stackargs)

    stack.parse.add_optional(key="run_timeout", default=4800, types="int")
    stack.parse.add_optional(key="label", default="clock probe", types="str")

    stack.add_substack("config0-hub:::config0_core::empty_stack")

    stack.init_variables()
    stack.init_substacks()

    stack.empty_stack.insert(display=True,
                             arguments={"description": f"{stack.label} run_timeout {stack.run_timeout}"},
                             human_description=f"{stack.label}: run_timeout {stack.run_timeout}")

    return stack.get_results()
