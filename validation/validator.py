import numpy as np

from simulation.environment_variables import Environment_Variables
from simulation.pricing_variables import Pricing_Variables
from simulation.other_variables import Other_Variables

from simulation.simulation import exec_simulation_multiple

from enum import Enum

import copy



class Validator:
    def __init__(self, ev, pv, ov, perc_honest_defectors):
        # accept an environment variables, pricing variables, and other variables
        # object for running the simulation within this class instance. We make a
        # copy since we'll be sampling the variables
        self.ev = copy.deepcopy(ev)
        self.pv = copy.deepcopy(pv)
        self.ov = copy.deepcopy(ov)
        
        self.ev.perc_honest_defectors = perc_honest_defectors
        
        # where the average will be stored
        self.running_avg = None
        
        # this dict will enumerate all of the attributes we want to sample while
        # running validation, but will also make use of it to store the average
        # sampled values
        self.ev_vars_to_sample = {
            # attribute         avg
            "chance_of_claim" : 0,
            "perc_low_morale": 0,
            "perc_independent": 0,
        }

        self.pv_vars_to_sample = {
            # attribute         avg
            "noref_change_floor"        : 0,
            "noref_change_ceiling"      : 0,
            "noref_ph_leave_floor"      : 0,
            "noref_ph_leave_ceiling"    : 0,
            "avg_3mo_change_floor"      : 0,
            "avg_3mo_change_ceiling"    : 0,
            "avg_3mo_ph_leave_floor"    : 0,
            "avg_3mo_ph_leave_ceiling"  : 0,
        }

    def validate(self, maxsd=3):
        self.running_avg = 0
        
        for i in range(self.ov.validator_num_samples):
            ev = Environment_Variables.sample(self.ev_vars_to_sample.keys(), maxsd)
            pv = Pricing_Variables.sample(self.pv_vars_to_sample.keys(), maxsd)
            results = exec_simulation_multiple(ev, pv, self.ov.validator_sample_size)
            self.running_avg += results.num_wins
        
        self.running_avg /= (self.ov.validator_num_samples * self.ov.validator_sample_size)
        return self.running_avg

