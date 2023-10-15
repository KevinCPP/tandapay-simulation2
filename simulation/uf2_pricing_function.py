import sys

from .environment_variables import Environment_Variables
from .pricing_variables import Pricing_Variables
from .system_record import System_Record
from .user_record import *
from .remove_user import remove_user
from .remove_user import evaluate_probability
import random

def uf2_pricing_function(ev, sr, pv, user_list, cur_period):
    """
    user function 2; pricing function

    :param ev: takes in simulation environment variables
    :param sr: takes in simulation system record
    :param pv: takes in simulation pricing variables
    :param user_list: takes in user list for this simulation instance
    :param cur_period: current period the simulation is on
    """

    # 1. Get a list of all active users
    list_of_active = []
    for i, user in enumerate(user_list):
        if user.sbg_status == ValidityEnum.VALID:
            list_of_active.append(i)

    leave_list = []
    for i in list_of_active:
        user = user_list[i]
        if user.total_value_refund_list[cur_period] == 0:
            if evaluate_noref(ev, pv, user, cur_period):
                leave_list.append(i)
#NOTE: Temporarily disabled this section
#        else:
#            if evaluate_refund(ev, pv, user, cur_period):
#                leave_list.append(i)
    
#    print(f"sizeof leave list: {len(leave_list)}")
    for i in leave_list:
        sr.valid_remaining -= 1
        sr.skipped_cnt += 1
        remove_user(user_list, i, "user was in leave list in uf2")

def evaluate_qualifying(ev, user, floor, cur_period):
    """
    evaluates if member is qualifying to be evaluated for uf2

    :param ev: environment variables for this simulation run
    :param user: user to evaluate
    :param floor: floor to calculate threshold from
    :param cur_period: current period simulation is on

    :return: threshold < second premium calc
    """
    threshold = floor * ev.monthly_premium    
    return threshold < user.second_premium_calc_list[cur_period]

# a, b, c, d correspond to steps in the spec. x is a step I changed to improve the code.
# evaluates a user who got no refund. Returns true if they are to be added to the leave list
def evaluate_noref(ev, pv, user, cur_period) -> bool:
    """
    evaluates member who did not get a refund

    :param ev: environment variables for this simulation run
    :param user: user to evaluate
    :param floor: floor to calculate threshold from
    :param cur_period: current period simulation is on
    
    :return: true if they defect
    """

    # test if they qualify
#    if not evaluate_qualifying(ev, user, pv.noref_change_floor, cur_period):
#        return False

    # find most recent period with a matching refund
    matching = find_previous_matching_refund(user, cur_period)
    pmp = 0
    if matching != -1:
        pmp = user.second_premium_calc_list[matching]
    else: 
        print(f"matching not found")
        pmp = ev.monthly_premium

    # calculate noref_cmp_floor and ceiling:
    cmp = user.second_premium_calc_list[cur_period]
    noref_cmp_floor = pmp * (1 + pv.noref_change_floor)
    noref_cmp_ceiling = pmp * (1 + pv.noref_change_ceiling)
    
    if cmp < noref_cmp_floor:
        return False

    # calculate noref pricing slope
    noref_pricing_slope = (pv.noref_ph_leave_ceiling - pv.noref_ph_leave_floor) / (pv.noref_change_ceiling - pv.noref_change_floor)
    
    if noref_cmp_ceiling < cmp:
        user.second_premium_calc_list[cur_period] = noref_cmp_ceiling
        cmp = user.second_premium_calc_list[cur_period]
    
    if noref_cmp_floor < cmp:
        noref_cmp_inc_percent = (cmp / pmp) - 1
        #print(f"cmp = {cmp}, pmp = {pmp}, noref_cmp_inc_perc = {noref_cmp_inc_percent}, matching = {matching}")
        noref_ph_leave_percent =  (noref_pricing_slope * noref_cmp_inc_percent)
        noref_ph_leave_percent -= (noref_pricing_slope * pv.noref_change_floor)
        noref_ph_leave_percent += pv.noref_ph_leave_floor
        #print(f"noref_ph_leave_percent | noref_pricing_slope | noref_cmp_inc_percent | noref_change_floor | noref_ph_leave_floor: {noref_ph_leave_percent}|{noref_pricing_slope}|{noref_cmp_inc_percent}|{pv.noref_change_floor}|{pv.noref_ph_leave_floor}")
        return evaluate_probability(noref_ph_leave_percent)
    else:
        return evaluate_cumulative(ev, pv, user, cur_period)

def evaluate_refund(ev, pv, user, cur_period) -> bool:
    """
    Unused function. disabled per Josh's recommendation to improve simulation results
    """
    # test if they qualify
#    if not evaluate_qualifying(ev, user, pv.refund_change_floor, cur_period):
#        return False

    # calculate refund_cmp_floor and refund_cmp_ceiling
    cmp = user.second_premium_calc_list[cur_period]
    refund_cmp_floor = ev.monthly_premium * pv.refund_change_floor
    refund_cmp_ceiling = ev.monthly_premium * pv.refund_change_ceiling
    
    # test if they qualify
    if cmp < refund_cmp_floor:
        return False

    # calculate refund pricing slope
    refund_pricing_slope = (pv.refund_ph_leave_ceiling - pv.refund_ph_leave_floor) / (pv.refund_change_ceiling - pv.refund_change_floor)
    
    # evaluate cap
    if refund_cmp_ceiling < cmp:
        user.second_premium_calc_list[cur_period] = refund_cmp_ceiling
        cmp = user.second_premium_calc_list[cur_period]

    # compare the second premium calc with the floor
    if refund_cmp_floor < cmp:
        refund_cmp_inc_percent = (cmp / refund_cmp_floor) - 1
        refund_ph_leave_percent =  (refund_pricing_slope * refund_cmp_inc_percent)
        refund_ph_leave_percent -= (refund_pricing_slope * pv.refund_change_floor)
        refund_ph_leave_percent += pv.refund_ph_leave_floor

        return evaluate_probability(refund_ph_leave_percent)
    else:
        return evaluate_cumulative(ev, pv, user, cur_period)

def evaluate_cumulative(ev, pv, user, cur_period) -> bool:
    """
    evaluates cumulative increase to determine if user defects

    :param ev: environment variables for this simulation run
    :param user: user to evaluate
    :param floor: floor to calculate threshold from
    :param cur_period: current period simulation is on

    :return: true if they defect
    """
    # constants for average calculation
    MIN_PERIOD = 4
    MAX_PERIOD = 9
    NUM_MONTHS_TO_AVG = 3

    # test if they qualify
#    if not evaluate_qualifying(ev, user, pv.avg_3mo_change_floor, cur_period):
#        return False
    
    # calculate avg_3mo_floor and avg_3mo_ceiling
    avg_3mo_floor = ev.monthly_premium * ev.chance_of_claim * (1.0 + pv.avg_3mo_change_floor)
    avg_3mo_ceiling = ev.monthly_premium * ev.chance_of_claim * (1.0 + pv.avg_3mo_change_ceiling)

    # calculate avg_3mo_pricing_slope
    avg_3mo_pricing_slope =  (pv.avg_3mo_ph_leave_ceiling - pv.avg_3mo_ph_leave_floor)
    avg_3mo_pricing_slope /= (pv.avg_3mo_change_ceiling - pv.avg_3mo_change_floor)
    
    # calculate the avergae
    avg = 0
    for i in range(cur_period, cur_period - NUM_MONTHS_TO_AVG, -1):
        avg += user.second_premium_calc_list[i] / NUM_MONTHS_TO_AVG
   
    # evaluate cap
    if avg_3mo_ceiling < avg:
        avg = avg_3mo_ceiling

    # roll the dice
    if avg_3mo_floor < avg:
        avg_3mo_cmp_inc_percent = (avg / (ev.monthly_premium * ev.chance_of_claim)) - 1
        avg_3mo_ph_leave_percent =  (avg_3mo_pricing_slope * avg_3mo_cmp_inc_percent)
        avg_3mo_ph_leave_percent -= (avg_3mo_pricing_slope * pv.avg_3mo_change_floor)
        avg_3mo_ph_leave_percent += pv.avg_3mo_ph_leave_floor
        return evaluate_probability(avg_3mo_ph_leave_percent)
    
    # return false if 3mo_avg_floor > avg
    return False

# iterates backwards to find matching refund
def find_previous_matching_refund(user, cur_period) -> int:
    for i in range(cur_period - 1, -1, -1):
        if user.total_value_refund_list[i] == user.total_value_refund_list[cur_period]:
            return i

    return -1
