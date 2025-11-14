import aviary.api as av
import matplotlib.pyplot as plt
import numpy as np
import openmdao.api as om
from aviary.variable_info.variables import Mission
from icecream import ic
from aviary.subsystems.subsystem_builder_base import SubsystemBuilderBase
from aviary.utils.aviary_values import AviaryValues

# import variables
from variables import Aircraft
from copy import deepcopy


class CostComponent(om.ExplicitComponent):
    # something that evaluates a function! but using openMDAO structure
    def initialize(self):
        # do ths for variables you don't want the optimizer to change
        self.options.declare("t_year", default=2030, types=int)
        self.options.declare("b_year", default=1989, types=int)

    def setup(self):
        # design variables
        # self.add_input("MTOW", val=60_000.0)
        # self.add_input("t_year", val=2030)
        # self.add_input("b_year", val=1989)
        self.add_input(Mission.GROSS_MASS, units="lbm")

        # output
        self.add_output(Aircraft.Cost.COST_FLYAWAY)

        self.declare_partials("*", "*", method="fd")
        # self.declare_partials(Aircraft.Cost.COST_FLYAWAY, Mission.GROSS_MASS)

    # def compute_partials(self, inputs, partials):
    # partials[Aircraft.Cost.COST_FLYAWAY, Mission.GROSS_MASS] = 0.8043 * C /

    def cef(self, t_year, b_year):
        b_cef = 5.1703 + 0.104891 * (b_year - 2006)
        t_cef = 5.1703 + 0.104891 * (t_year - 2006)

        return t_cef / b_cef

    def compute(self, inputs, outputs={}):
        mtow = inputs["MTOW"]
        mtow = inputs[Mission.Summary.GROSS_MASS]
        t_year = self.options["t_year"]
        b_year = self.options["b_year"]

        cef = self.cef(t_year, b_year)

        outputs[Aircraft.Cost.COST_FLYAWAY] = (
            10 ** (3.3191 + 0.8043 * np.log(mtow)) * cef
        )
        # return outputs["cost"]


class CostBuilder(SubsystemBuilderBase):
    def __init__(self, name="cost"):
        super().__init__(name)

    # this is a post mission component only, because cost is only important after mission analysis
    def build_post_mission(self, aviary_inputs=AviaryValues(), **kwargs):
        cost_calcs = om.Group()
        cost_calcs.add_subssystem(
            "cost_flyaway_calc",
            CostComponent(),
            promotes_inputs=["mission:*"],
            promotes_outputs=[Aircraft.Cost.COST_FLYAWAY],
        )
        return cost_calcs


def main(save=True):
    prob = om.Problem()
    prob.model.add_subsystem("cost_comp", CostComponent(), promotes=["*"])

    mtow = np.linspace(60000, 1000000, 100)
    cost = []
    for mtow_val in mtow:
        comp = CostComponent()
        comp.setup()
        inputs = {"MTOW": mtow_val, "t_year": 2025, "b_year": 1989}
        output = comp.compute(inputs)
        cost.append(output)

    fig, ax = plt.subplots()
    ax.plot(mtow, cost)
    ax.set_xlabel("MTOW (lbs)")
    ax.set_ylabel("Cost ($)")
    ax.grid(True)
    ax.set_title(
        f"Aircraft Cost vs MTOW: t_year={inputs['t_year']}, b_year={inputs['b_year']}"
    )
    if save:
        plt.savefig("cost_vs_mtow.png")
    else:
        plt.show()


def run():
    prob = av.AviaryProblem()
    prob.load_inputs(
        "models/aircraft/test_aircraft/aircraft_for_bench_FwFm.csv",
        phase_info,
    )
    prob.check_and_preprocess_inputs()
    prob.build_model()

    prob.add_driver("SLSQP")

    prob.add_design_variables()

    # prob.add_objective()
    prob.model.add_objective(Aircraft.Cost.COST_FLYAWAY, ref=1e6)

    prob.setup()

    prob.run_aviary_problem(suppress_solver_print=True)

    ic(prob.get_val(av.Mission.Summary.GROSS_MASS))
    ic(prob.get_val(Aircraft.Cost.COST_FLYAWAY))


if __name__ == "__main__":
    # main()
    run()
