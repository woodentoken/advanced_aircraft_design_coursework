import matplotlib.pyplot as plt
import numpy as np
import openmdao.api as om
from icecream import ic


def get_results(filename):
    cr = om.CaseReader(filename)
    cases = cr.get_cases()

    results = {}
    for case in cases:
        for key in case.outputs.keys():
            if key not in results.keys():
                results[key] = []
            results[key].append(case.outputs[key])

    for key in case.outputs.keys():
        results[key] = np.array(results[key])

    return results


def main(unconstrained=False, constrained=False, quiz=False, inclass=False):
    if all([not unconstrained, not constrained, not quiz, not inclass]):
        print("Please select at least one problem to run")
        return

    if unconstrained:

        def unconstrained():
            print("### unconstrained problem ###")
            ## Unconstrained optimization
            excomp = om.ExecComp("obj=(x**2 + y - 11)**2 + (x + y**2 -7)**2")

            unconstrained_prob = om.Problem()
            unconstrained_prob.model.add_subsystem("excomp", excomp, promotes=["*"])

            # setup the optimization
            unconstrained_prob.driver = om.ScipyOptimizeDriver()
            unconstrained_prob.driver.options["optimizer"] = "SLSQP"
            unconstrained_prob.driver.options["tol"] = 1.0e-9
            unconstrained_prob.driver.recording_options["includes"] = ["*"]
            unconstrained_recorder = om.SqliteRecorder("unconstrained.sql")
            unconstrained_prob.driver.add_recorder(unconstrained_recorder)
            unconstrained_prob.model.add_design_var("x", lower=-4.0, upper=4.0)
            unconstrained_prob.model.add_design_var("y", lower=-4.0, upper=4.0)
            unconstrained_prob.model.add_objective("obj")
            unconstrained_prob.setup()

            # run the optimization
            unconstrained_prob.run_driver()

            unconstrained_results = get_results("test_out/unconstrained.sql")
            ic(unconstrained_results)

    if constrained:

        def constrained():
            print("### constrained problem ###")
            ## Constrained optimization
            constrained_prob = om.Problem()
            constrained_prob.model.add_subsystem("excomp", excomp, promotes=["*"])
            constrained_prob.model.add_subsystem(
                "constraint_comp", constraint_comp, promotes=["*"]
            )

            constraint_comp = om.ExecComp("con=x**2 + y**2")

            # setup the optimization
            constrained_prob.driver = om.ScipyOptimizeDriver()
            constrained_prob.driver.options["optimizer"] = "SLSQP"
            constrained_prob.driver.options["tol"] = 1.0e-9
            constrained_prob.driver.recording_options["includes"] = ["*"]
            constrained_recorder = om.SqliteRecorder("constrained.sql")
            constrained_prob.driver.add_recorder(constrained_recorder)
            constrained_prob.model.add_design_var("x", lower=-4.0, upper=4.0)
            constrained_prob.model.add_design_var("y", lower=-4.0, upper=4.0)
            constrained_prob.model.add_constraint("con", upper=4)
            constrained_prob.model.add_objective("obj")
            constrained_prob.setup()

            # run the optimization
            constrained_prob.run_driver()

            constrained_results = get_results("test2_out/constrained.sql")
            ic(constrained_results)

    if quiz:

        def quiz():
            print("### quiz problem ###")
            # quiz problem specifically
            quiz_problem = om.Problem()
            # quiz_function =
            quiz_problem.model.add_subsystem(
                "quiz_function",
                om.ExecComp("f=(x-4)**2 + x*y + (y+3)**2 - 3"),
                promotes=["*"],
            )

            quiz_problem.driver = om.ScipyOptimizeDriver()
            quiz_problem.driver.options["optimizer"] = "Nelder-Mead"
            ic(quiz_problem.driver.options["optimizer"])

            # quiz_problem.driver.options["tol"] = 1.0e-9
            ic(quiz_problem.driver.options["tol"])
            quiz_problem.model.add_design_var("x", lower=-50.0, upper=50.0)
            quiz_problem.model.add_design_var("y", lower=-50.0, upper=50.0)
            quiz_problem.model.add_objective("f")
            quiz_problem.setup()
            quiz_problem.set_val("x", 3.0)
            quiz_problem.set_val("y", -4.0)

            # run the optimization
            quiz_problem.run_driver()
            ic(quiz_problem.get_val("x"))
            ic(quiz_problem.get_val("y"))
            ic(quiz_problem.get_val("f"))
            quiz_results = get_results("mdao_basics_out/quiz_problem.sql")

            ic(quiz_results)

    if inclass:

        def inclass():
            print("### inclass problem ###")
            inclass_problem = om.Problem()
            # function has a large number of local minima
            inclass_problem.model.add_subsystem(
                "inclass",
                om.ExecComp(
                    "f = 0.1*(x+y) - abs( sin(x) * cos(y) * exp( abs( 1 - (x**2 + y**2)**(0.5) / pi ) ))",
                ),
            )
            inclass_problem.driver = om.ScipyOptimizeDriver()
            inclass_problem.driver.options["optimizer"] = "SLSQP"
            inclass_problem.model.add_design_var(
                "inclass.x", lower=-1000.0, upper=1000.0
            )
            inclass_problem.model.add_design_var(
                "inclass.y", lower=-1000.0, upper=1000.0
            )
            inclass_problem.model.add_objective("inclass.f")
            inclass_problem.setup()
            inclass_problem.set_val("inclass.x", 20.0)
            inclass_problem.set_val("inclass.y", -20.0)
            inclass_problem.run_driver()
            ic(inclass_problem.get_val("inclass.x"))
            ic(inclass_problem.get_val("inclass.y"))
            ic(inclass_problem.get_val("inclass.f"))


if __name__ == "__main__":
    main(inclass=True)
