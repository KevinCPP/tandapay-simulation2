import numpy as np

from simulation.environment_variables import Environment_Variables
from simulation.pricing_variables import Pricing_Variables
from simulation.other_variables import Other_Variables

from simulation.simulation import exec_simulation_multiple

from enum import Enum

import copy



class Validator:
    def __init__(self, ov, perc_honest_defectors):
        # other variables object, will contain information such as the
        # sample size, number of trials, and the max standard deviations
        self.ov = ov
        
        # defector value that we want to validate
        self.perc_honest_defectors = perc_honest_defectors
        
        # where the average will be stored
        self.running_avg = None
        
        # EV attributes we want to sample
        self.ev_vars_to_sample = [
            "chance_of_claim",
            "perc_low_morale",
            "perc_independent",
        ]
        
        # PV attributes we want to sample
        self.pv_vars_to_sample = [
            "noref_change_floor",
            "noref_change_ceiling",
            "noref_ph_leave_floor",
            "noref_ph_leave_ceiling",
            "avg_3mo_change_floor",
            "avg_3mo_change_ceiling",
            "avg_3mo_ph_leave_floor",
            "avg_3mo_ph_leave_ceiling",
        ]

    def validate(self):
        self.running_avg = 0
        
        for i in range(self.ov.validator_num_samples):
            ev = Environment_Variables.sample(self.ev_vars_to_sample, self.ov.maxsd)
            ev.perc_honest_defectors = self.perc_honest_defectors
            pv = Pricing_Variables.sample(self.pv_vars_to_sample, self.ov.maxsd)
            results = exec_simulation_multiple(ev, pv, self.ov.validator_sample_size)
            self.running_avg += results.num_wins
        
        self.running_avg /= (self.ov.validator_num_samples * self.ov.validator_sample_size)
        return self.running_avg

