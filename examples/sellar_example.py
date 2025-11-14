import numpy as np
import openmdao.api as om
from icecream import ic


# first discipline's problem/process
class SellarDiscipline1(om.ExplicitComponent):
    def setup(self):
        # design variables
        self.add_input("z", val=np.zeros(2))
        self.add_input("x", val=0.0)

        # coupling parameter - not a design variable
        self.add_input("y2", val=1.0)

        # outputs
        self.add_output("y1", val=1.0)

    def setup_partials(self):
        self.declare_partials("*", "*", method="cs")

    def compute(self, inputs, outputs):
        # this is just convenience
        z1 = inputs["z"][0]
        z2 = inputs["z"][1]
        x1 = inputs["x"]
        y2 = inputs["y2"]

        outputs["y1"] = z1**2 + z2 + x1 - 0.2 * y2


# second discipline's problem/process
class SellarDiscipline2(om.ExplicitComponent):
    def setup(self):
        self.add_input("z", val=np.zeros(2))
        self.add_input("y1", val=1.0)
        self.add_output("y2", val=1.0)

    def setup_partials(self):
        self.declare_partials("*", "*", method="cs")

    def compute(self, inputs, outputs):
        z1 = inputs["z"][0]
        z2 = inputs["z"][1]
        y1 = inputs["y1"]

        # defend against negative sqrt
        if y1.real < 0.0:
            y1 *= -1.0

        outputs["y2"] = y1**0.5 + z1 + z2


# create a group to contain the disciplines and the connections between them
class SellarConnection(om.Group):
    def setup(self):
        connection = self.add_subsystem("connection", om.Group(), promotes=["*"])
        connection.add_subsystem(
            "d1",
            SellarDiscipline1(),
            promotes=["*"],
            # promotes_inputs=["z", "x", "y2"],
            # promotes_outputs=["y1"],
        )
        connection.add_subsystem(
            "d2",
            SellarDiscipline2(),
            promotes=["*"],
            # promotes_inputs=["z", "y1"],
            # promotes_outputs=["y2"],
        )

        connection.set_input_defaults("x", 1.0)
        connection.set_input_defaults("z", np.array([5.0, 2.0]))

        connection.nonlinear_solver = om.NonlinearBlockGS()
        connection.nonlinear_solver.options["iprint"] = 2
        connection.nonlinear_solver.options["maxiter"] = 100
        connection.nonlinear_solver.options["debug_print"] = True
        connection.linear_solver = om.ScipyKrylov()
        # connection.nonlinear_solver.options["err_on_non_converge"] = True

        # add the objective
        self.add_subsystem(
            "objective_cmp",
            om.ExecComp(
                "objective = x**2 + z[1] + y1 + exp(-y2)", z=np.array([0.0, 0.0]), x=0.0
            ),
            promotes=["x", "z", "y1", "y2", "objective"],
        )
        # add the constraints
        # equality constraint on y1
        self.add_subsystem(
            "con_cmp1", om.ExecComp("con1 = y1"), promotes=["y1", "con1"]
        )
        # equality constraint on y2
        self.add_subsystem(
            "con_cmp2", om.ExecComp("con2 = y2"), promotes=["y2", "con2"]
        )


def main(solve=False, optimize=True):
    prob = om.Problem()
    # use the group as the model for the problem
    prob.model = SellarConnection()

    if solve:
        print("SOLVE ONLY")
        prob.setup()

        prob.set_val("x", 2.0)
        prob.set_val("z", np.array([-1.0, -1.0]))

        prob.run_model()
        # prob.check_partials(compact_print=True)

        ic(prob.get_val("x"))
        ic(prob.get_val("z"))
        ic(prob.get_val("y1"))
        ic(prob.get_val("y2"))

    if optimize:
        print("OPTIMIZE")
        prob.driver = om.ScipyOptimizeDriver()
        prob.driver.options["optimizer"] = "SLSQP"
        prob.driver.options["debug_print"] = ["desvars", "nl_cons", "objs"]
        prob.driver.options["tol"] = 1e-8

        prob.driver.add_recorder(om.SqliteRecorder("cases.sql"))
        prob.driver.recording_options["record_desvars"] = True
        prob.driver.recording_options["record_objectives"] = True
        prob.driver.recording_options["record_constraints"] = True

        prob.model.add_design_var("x", lower=0.0, upper=10.0)
        prob.model.add_design_var("z", lower=0.0, upper=10.0)

        prob.model.add_objective("objective")
        prob.model.add_constraint("con1", lower=3.16)
        prob.model.add_constraint("con2", upper=24.0)

        # this is needed for openMDAO to compute total derivatives across the disciplines
        prob.setup()
        prob.set_solver_print(level=0)

        prob.model.approx_totals()
        prob.check_partials(method="fd", compact_print=True)
        prob.check_totals(method="cs", compact_print=True)

        # run the optimization
        prob.run_driver()

        prob.model.list_outputs(prom_name=True)

        ic(prob.get_val("x"))
        ic(prob.get_val("z"))
        # ic(prob.get_val("y1"))
        # ic(prob.get_val("y2"))
        ic(prob.get_val("con1"))
        ic(prob.get_val("con2"))
        ic(prob.get_val("objective"))


if __name__ == "__main__":
    main(solve=True, optimize=True)
