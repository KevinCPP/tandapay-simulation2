import numpy as np

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
            "chance_of_claim" : 0
            "perc_low_moreale": 0
            "perc_independent": 0
        }

        self.pv_vars_to_sample = {
            # attribute         avg

        }

    def validate(self):
         
