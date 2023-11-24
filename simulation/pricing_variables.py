import random
from util.biased_random import biased_random

class Pricing_Variables:
    """
    Encapsulates the pricing variables we are running the simulation with
    """
    def __init__(self):
        self.noref_change_floor         = .10
        self.noref_change_ceiling       = .90
        self.noref_ph_leave_floor       = .05
        self.noref_ph_leave_ceiling     = .30

        self.refund_change_floor        = .35
        self.refund_change_ceiling      = .60
        self.refund_ph_leave_floor      = .04
        self.refund_ph_leave_ceiling    = .08

        self.avg_3mo_change_floor       = .50
        self.avg_3mo_change_ceiling     = .80
        self.avg_3mo_ph_leave_floor     = .02
        self.avg_3mo_ph_leave_ceiling   = .04
   
    @staticmethod
    def get_limits(attribute: str):
        attr_limits = {
            "noref_change_floor"        : (0, 0.50),
            "noref_change_ceiling"      : (0.50, 1),
            "noref_ph_leave_floor"      : (0.01, 0.09),
            "noref_ph_leave_ceiling"    : (0.20, 0.40),
            "avg_3mo_change_floor"      : (0, 0.50),
            "avg_3mo_change_ceiling"    : (0.50, 1),
            "avg_3mo_ph_leave_floor"    : (0.01, 0.3),
            "avg_3mo_ph_leave_ceiling"  : (0.03, 0.05),
        }
        
        if attribute in attr_limits:
            return attr_limits[attribute]

        return (0, 1)
    
    @staticmethod
    def sample(max_sd=3):
        pv = Pricing_Variables()
        
        limits = get_limits("noref_change_floor")
        pv.noref_change_floor = biased_random(limits[0], limits[1], pv.noref_change_floor, max_sd) 
        limits = get_limits("noref_change_ceiling")
        pv.noref_change_ceiling = biased_random(limits[0], limits[1], pv.noref_change_ceiling, max_sd)
        limits = get_limits("noref_ph_leave_floor")
        pv.noref_ph_leave_floor = biased_random(limits[0], limits[1], pv.noref_change_ceiling, max_sd)
        limits = get_limits("noref_ph_leave_ceiling")
        pv.noref_ph_leave_ceiling = biased_random(limits[0], limits[1], pv.noref_ph_leave_ceiling, max_sd)
        limits = get_limits("avg_3mo_change_floor")
        pv.avg_3mo_change_floor = biased_random(limits[0], limits[1], pv.avg_3mo_change_floor, max_sd)
        limits = get_limits("avg_3mo_change_ceiling")
        pv.avg_3mo_change_ceiling = biased_random(limits[0], limits[1], pv.avg_3mo_change_ceiling, max_sd)
        limits = get_limits("avg_3mo_ph_leave_floor")
        pv.avg_3mo_ph_leave_floor = biased_random(limits[0], limits[1], pv.avg_3mo_ph_leave_floor, max_sd)
        limits = get_limits("avg_3mo_ph_leave_ceiling")
        pv.avg_3mo_ph_leave_ceiling = biased_random(limits[0], limits[1], pv.avg_3mo_ph_leave_ceiling, max_sd)
        
        return pv
         
