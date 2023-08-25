import copy
import os
import shutil
import time
from datetime import datetime
import random
from settings import RESULT_DIR
from utils.common import write_csv
from utils.logger import logger


class TandaPaySimulatorV2(object):

    def __init__(self, ev=None, pv=None, count=10, bundling=0, matrix=False):
        self.ev = ev or {}
        self.cov_req = ev['cov_req']
        self._total = ev['total_member_cnt']
        self.pv = pv or {}
        self.period = 0
        self.matrix = matrix
        self.bundling = bundling
        self.count = count
        self.usr = [
            {
                'orig_sbg_num': 0,
                'remaining_orig_sbg': 0,
                'cur_sbg_num': 0,
                'members_cur_sbg': 0,
                'sbg_reorg_cnt': 0,
                'pri_role': '',
                'sec_role': '',
                'cur_status': 'valid',
                'reorged_cnt': 0,
                'payable': 'yes',
                'defector_cnt': 0,
                'cur_mon_balance': 0,
                'cur_mon_premium': 0,
                'cur_mon_1st_calc': 0,
                'cur_mon_sec_cals': [0, ] * count,
                'total_value_refunds': [0, ] * count,
                'wallet_balance': 0,
                'wallet_claim_award': 0,
                'wallet_no_claim_refund': 0,
                'wallet_reorg_refund': 0,
                'prior_premiums': [0] * max(self.bundling, 1),
                'debit_to_savings_account': [0., ] * count,
            } for _ in range(ev['total_member_cnt'])]

        self.sys = [
            {
                'valid_remaining': ev['total_member_cnt'],
                'defected_cnt': 0,
                'skipped_cnt': 0,
                'invalid_cnt': 0,
                'quit_cnt': 0,
                'reorged_cnt': 0,
                'defection_sf': 0,
                'skip_sf': 0,
                'invalid_sf': 0,
                'cur_mon_1st_calc': 0,
                'total_sf_period_one_claim': 0,
                'cur_mon_total_sf': 0,
                'individual_sf_period_one_claim': 0,
                'cur_mon_individual_sf': 0,
                'claimed': False,
            } for _ in range(count)
        ]

    def _active_users(self):
        return [i for i in range(self._total) if self.usr[i]['cur_status'] == 'valid']


    def start_simulation(self, target_dir=RESULT_DIR):
        s_time = time.time();
        target_dir = os.path.join(target_dir, datetime.now().strftime('%m_%d_%Y__%H_%M_%S'))
        os.makedirs(target_dir, exist_ok=True)

        logger.debug(f"Total members in the group: {self._total}")

        temp_val_four = self.subgroup_setup()

        self.role_assignment(temp_val_four)

        # ========================================= Period =========================================
        for self.period in range(self.count):
            if self.period > 0:
                self.sys[self.period]['valid_remaining'] = self.sys[self.period - 1]['valid_remaining']
            # RsA
            cur_mon_1st_calc = self.cov_req / self.sys[self.period]['valid_remaining']
            self.sys[self.period]['cur_mon_1st_calc'] = cur_mon_1st_calc
            for i in self._active_users():
                # Current mons First Premium Calculation
                self.usr[i]['cur_mon_1st_calc'] = cur_mon_1st_calc
                if self.period == 0:
                    self.usr[i]['cur_mon_sec_cals'][0] = cur_mon_1st_calc
                else:
                    wallet_balance = cur_mon_1st_calc + self.usr[i]['debit_to_savings_account'][self.period - 1] - \
                        self.usr[i]['wallet_no_claim_refund'] - self.usr[i]['wallet_reorg_refund']
                    wallet_balance = max(wallet_balance, 0)
                    self.usr[i]['wallet_balance'] = wallet_balance
                    self.usr[i]['cur_mon_sec_cals'][self.period] = wallet_balance

                self.usr[i]['total_value_refunds'][self.period] = \
                    self.usr[i]['wallet_no_claim_refund'] + self.usr[i]['wallet_reorg_refund'] + \
                    self.usr[i]['wallet_claim_award']

            if self.period == 0:       # Period 1
                self.user_func_1()
            else:
                self.user_func_2()

            # RsB
            for i in self._active_users():
                if self.period == 0:
                    self.usr[i]['cur_mon_balance'] += self.usr[i]['cur_mon_1st_calc']
                else:
                    if self.usr[i]['cur_mon_balance'] > self.usr[i]['cur_mon_1st_calc']:
                        self.usr[i]['cur_mon_balance'] = self.usr[i]['cur_mon_sec_cals'][self.period] - \
                            self.usr[i]['debit_to_savings_account'][self.period - 1]
                        self.usr[i]['debit_to_savings_account'][self.period] = 0
                    elif self.usr[i]['cur_mon_balance'] < self.usr[i]['cur_mon_1st_calc']:
                        self.usr[i]['cur_mon_balance'] = self.usr[i]['cur_mon_1st_calc']

                    if self.usr[i]['cur_mon_balance'] != self.usr[i]['cur_mon_1st_calc']:
                        logger.error(f"Balance not matching with 1st calc for user{i}")

            self.sys_func_4()

            self.user_func_6()

            self.rsc()

            cmb = sum([self.usr[i]['cur_mon_balance'] for i in self._active_users()])
            if abs(cmb - self.cov_req) > .1:
                logger.warning([self.usr[i]['cur_mon_balance'] for i in self._active_users()])
                logger.error(f">>> Invalid mon balance: {cmb}, CR: {self.cov_req}, active: {len(self._active_users())}")
                break

            self.sys_func_8()

            self.sys_func_7()

            # Queuing(Bundling) Function
            if self.bundling > 0 and self.sys[self.period]['claimed']:
                logger.info(f"Claim occurred in period {self.period + 1}")
            else:
                for i in self._active_users():
                    if self.bundling in {0, 2}:
                        self.usr[i]['wallet_no_claim_refund'] = self.usr[i]['prior_premiums'][0]
                    elif self.bundling == 3:
                        self.usr[i]['wallet_no_claim_refund'] = self.usr[i]['prior_premiums'][1]
                        self.usr[i]['prior_premiums'][1] = self.usr[i]['prior_premiums'][0]
                    elif self.bundling == 4:
                        self.usr[i]['wallet_no_claim_refund'] = self.usr[i]['prior_premiums'][2]
                        self.usr[i]['prior_premiums'][2] = self.usr[i]['prior_premiums'][1]
                        self.usr[i]['prior_premiums'][1] = self.usr[i]['prior_premiums'][0]
                    self.usr[i]['prior_premiums'][0] = self.usr[i]['cur_mon_premium']
                    self.usr[i]['cur_mon_premium'] = 0

            if self.period > 1 and \
                    all([self.sys[i]['skipped_cnt'] == 0 for i in range(self.period, self.period - 3, -1)]) and \
                    all([self.sys[i]['quit_cnt'] == 0 for i in range(self.period, self.period - 3, -1)]):
                logger.warning(f"No skipped or quited users at period {self.period + 1}, something is wrong...")
                break

            logger.debug(f">>> Finished period {self.period + 1}, active users: {len(self._active_users())}")
            write_csv(data=self.usr, path=os.path.join(target_dir, f'Period {self.period + 1} User Database.csv'))
            write_csv(data=self.sys, path=os.path.join(target_dir, f'Period {self.period + 1} System Database.csv'))

        logger.info(f'Complete at period {self.period + 1}, elapsed: {time.time() - s_time}')

        write_csv(data=self.usr, path=os.path.join(target_dir, '1 User Database.csv'))
        write_csv(data=self.sys, path=os.path.join(target_dir, '1 System Database.csv'))

        defected = round(self.sys[self.period]['defected_cnt'] / self._total * 100, 2)
        inc_premium = round((self.sys[self.period]['cur_mon_total_sf'] /
                             self.sys[0]['cur_mon_total_sf']) * 100, 2)
        result_file = os.path.join(target_dir, "result.txt")
        results = [
            self._total,
            self.sys[self.period]['valid_remaining'],
            round(((self._total - self.sys[self.period]['valid_remaining']) / self._total) * 100, 2),
            self.sys[0]['cur_mon_total_sf'],
            self.sys[self.period]['cur_mon_total_sf'],
            inc_premium,
            self.sys[0]['defected_cnt'],
            self.ev['perc_honest_defectors'] * 100,
            defected,
            self.pv['prem_inc_cum'] * 100
        ]
        lines = [
            f'{self._total} is the number of members at the start of the simulation\n',
            f'{results[1]} is the number of valid members remaining at the end of the simulation\n',
            f'{results[2]}% of policyholders left the group by end of simulation\n',
            f'{results[3]} was the initial premium members were asked to pay.\n',
            f'{results[4]} is the final premium members were asked to pay.\n',
            f'Premiums increased by {results[5]}% by end of simulation\n',
            f'self.SyRec 3 (period 0 finalize) = {results[6]}\n',
            f'{results[7]}% of policyholders who were assigned to defect\n',
            f'{defected}% of policyholders who actually defected\n',
            f'{results[9]}% was the initial collapse threshold set for PV 5\n'
        ]
        logger.info('\n' + ''.join(lines))
        if not self.matrix:
            with open(result_file, 'w') as f:
                f.writelines(lines)
        else:
            shutil.rmtree(target_dir, ignore_errors=True)
        return results

    def subgroup_setup(self):
        # ============================== Subgroup Setup ========================================
        step1_ev1 = self._total
        step2 = self._total / 5
        step3 = round(step2 / 2.3333)
        step4 = step3 * 5
        step5 = step1_ev1 - step4
        step6 = step5 / 6
        step7 = round(step6 / 2)
        step8 = step7 * 6
        step9 = step5 - step8
        step10 = step9 / 7
        step11 = int(step10 / 2)
        step12 = step11 * 7
        step13 = step9 - step12
        step14 = int(step13 / 4)
        step15 = step13 % 4
        if step15 == 1:
            step3 -= 1
            step7 += 1
        elif step15 == 2:
            step3 -= 1
            step11 += 1
        elif step15 == 3:
            step3 -= 1
            step14 += 2

        # Assigning number to the group, condition checking for group == 4
        group_num = 1
        group_mem_count = 0
        temp_val_four = step14 * 4
        offset = 0
        for i in range(temp_val_four):
            self.usr[i + offset]['orig_sbg_num'] = group_num
            self.usr[i + offset]['remaining_orig_sbg'] = 4
            self.usr[i + offset]['cur_sbg_num'] = group_num
            self.usr[i + offset]['members_cur_sbg'] = 4
            group_mem_count += 1
            if group_mem_count == 4:
                group_num += 1
                group_mem_count = 0
        offset += temp_val_four

        # condition checking for group == 5
        temp_val_five = step3 * 5
        for i in range(temp_val_five):
            self.usr[i + offset]['orig_sbg_num'] = group_num
            self.usr[i + offset]['remaining_orig_sbg'] = 5
            self.usr[i + offset]['cur_sbg_num'] = group_num
            self.usr[i + offset]['members_cur_sbg'] = 5
            group_mem_count += 1
            if group_mem_count == 5:
                group_num += 1
                group_mem_count = 0
        offset += temp_val_five

        # condition checking for group == 6
        temp_val_six = step7 * 6
        for i in range(temp_val_six):
            self.usr[i + offset]['orig_sbg_num'] = group_num
            self.usr[i + offset]['remaining_orig_sbg'] = 6
            self.usr[i + offset]['cur_sbg_num'] = group_num
            self.usr[i + offset]['members_cur_sbg'] = 6
            group_mem_count += 1
            if group_mem_count == 6:
                group_num += 1
                group_mem_count = 0
        offset += temp_val_six

        # condition checking for group == 7
        temp_val_seven = step11 * 7
        for i in range(temp_val_seven):
            self.usr[i + offset]['orig_sbg_num'] = group_num
            self.usr[i + offset]['remaining_orig_sbg'] = 7
            self.usr[i + offset]['cur_sbg_num'] = group_num
            self.usr[i + offset]['members_cur_sbg'] = 7
            group_mem_count += 1
            if group_mem_count == 7:
                group_num += 1
                group_mem_count = 0

        checksum = offset + temp_val_seven
        if checksum != self._total:
            raise ValueError(f"Initial group checksum failed: checksum:{checksum} != EV1:{self._total}")
        logger.debug({"D": temp_val_four, "A": temp_val_five, "B": temp_val_six, "C": temp_val_seven})

        logger.debug(
            f'Group4 members: {step14}, Group5 members: {step3}, Group6 members: {step7}, '
            f'Group7 members: {step11}, Total group: {step14 * 4 + step3 * 5 + step7 * 6 + step11 * 7}')
        return temp_val_four

    def role_assignment(self, temp_val_four):
        # ========================================= Role Assignment =========================================
        # ROLE 1
        role_honest_defectors = int(self._total * self.ev['perc_honest_defectors'])
        defectors = random.sample(range(self._total), role_honest_defectors)
        non_defectors = [i for i in range(self._total) if i not in defectors]
        role_low_morale = int(self._total * self.ev['perc_low_morale'])
        low_morales = random.sample(non_defectors, role_low_morale)
        for i in range(self._total):
            self.usr[i]['pri_role'] = \
                'defector' if i in defectors else 'low-morale' if i in low_morales else 'unity-role'

        # ROLE 2
        # temp_val_four users and pick remaining users randomly to be equal with EV6
        # (percentage of members who are unwilling to act alone)
        remaining = int(self.ev['perc_independent'] * self._total) - temp_val_four
        rand_dep_user = random.sample(range(temp_val_four, self._total), remaining) if remaining > 0 else []
        for i in range(self._total):
            self.usr[i]['sec_role'] = 'dependent' if (i < temp_val_four or i in rand_dep_user) else 'independent'

    def user_func_1(self):
        """
        User defection function
        """
        for i in range(self._total):
            if self.usr[i]['pri_role'] == 'defector':
                defector_cnt = len([
                    u for u in self.usr
                    if u['pri_role'] == 'defector' and u['cur_sbg_num'] == self.usr[i]['cur_sbg_num']])
                self.usr[i]['defector_cnt'] = defector_cnt
                if self.usr[i]['sec_role'] == 'independent' or defector_cnt >= self.ev['dependent_thres']:
                    self.sys[self.period]['valid_remaining'] -= 1
                    self.sys[self.period]['defected_cnt'] += 1
                    self.sys[self.period]['skipped_cnt'] += 1
                    self.remove_usr(i)
                else:
                    self.usr[i]['pri_role'] = 'low-morale'
        s_d = self.sys[self.period]
        self.sys[self.period]['defection_sf'] = s_d['defected_cnt'] * s_d['cur_mon_1st_calc']
        self.sys[self.period]['skip_sf'] = s_d['skipped_cnt'] * s_d['cur_mon_1st_calc']

    def user_func_2(self):
        """"
        Pay Stage 2,  Pricing function
        """
        slope = (self.pv['ph_leave_ceiling'] - self.pv['ph_leave_floor']) / \
                (self.pv['prem_inc_ceiling'] - self.pv['prem_inc_floor'])
        leave_users = []
        for i in self._active_users():
            if self.usr[i]['total_value_refunds'][self.period] == 0:
                matches = [p for p in range(self.period - 1, -1, -1) if self.usr[i]['total_value_refunds'][p] == 0]
            else:
                matches = [p for p in range(self.period - 1, -1, -1) if self.usr[i]['total_value_refunds'][p] != 0]
            if not matches:
                logger.debug(f"User {i} - cannot find the matching period!")
                continue
            # print(f"The user number is {i}")
            # print(f"The current month sec calc for this period {self.usr[i]['cur_mon_sec_cals'][self.period]}")
            # print(f"The current month sec calc for matching period {self.usr[i]['cur_mon_sec_cals'][matches[-1]]}")
            if self.usr[i]['cur_mon_sec_cals'][self.period - 1] == 0:
                logger.warning(f"Pricing Function: User{i} sec cals in period {self.period} "
                               f"- {self.usr[i]['cur_mon_sec_cals']}")
                continue
            one_mon_inc_perc = \
                (self.usr[i]['cur_mon_sec_cals'][self.period] / self.usr[i]['cur_mon_sec_cals'][self.period - 1]) - 1
            # print(f"The one_month_inc_perc is {one_mon_inc_perc}")
            one_mon_inc_perc = min(one_mon_inc_perc, self.pv['prem_inc_ceiling'])
            if one_mon_inc_perc >= self.pv['prem_inc_floor']:
                ph_skip_perc = slope * (one_mon_inc_perc - self.pv['prem_inc_floor']) + self.pv['ph_leave_floor']
                if not self.pv['ph_leave_floor'] <= ph_skip_perc <= self.pv['ph_leave_ceiling']:
                    raise ValueError(f"Something is wrong with PH skip percentage - {ph_skip_perc}")
                rando = random.uniform(0, 1)
                if rando < ph_skip_perc:
                    # logger.debug(f'Run {self.period} PH Skip Pct: {ph_skip_perc} User: {i}, {one_mon_inc_perc}, '
                    #              f'Random num: {rando}')
                    leave_users.append(i)
                    continue
            cum_inc_perc = self.usr[i]['cur_mon_sec_cals'][self.period] / (self.cov_req / self._total) - 1
            if cum_inc_perc > self.pv['prem_inc_cum']:
                if random.uniform(0, 1) < self.pv['ph_leave_cum']:
                    leave_users.append(i)

        for i in leave_users:
            self.sys[self.period]['valid_remaining'] -= 1
            self.sys[self.period]['skipped_cnt'] += 1
            self.remove_usr(i, reason='pricing')
        sd = self.sys[self.period]
        self.sys[self.period]['skip_sf'] = sd['skipped_cnt'] * sd['cur_mon_1st_calc']

    def remove_usr(self, index, reason=''):
        logger.debug(f"Removing a user - {index}, reason: {reason}")
        for j in range(self._total):
            if self.usr[j]['cur_sbg_num'] == self.usr[index]['cur_sbg_num']:
                self.usr[j]['members_cur_sbg'] -= 1
            if self.usr[j]['orig_sbg_num'] == self.usr[index]['orig_sbg_num']:
                self.usr[j]['remaining_orig_sbg'] -= 1
        self.usr[index]['cur_sbg_num'] = 0
        self.usr[index]['members_cur_sbg'] = 0
        self.usr[index]['cur_status'] = 'NR'
        self.usr[index]['payable'] = 'NR'

    def sys_func_4(self):
        """"
        Invalidate subgroup function
        """
        for i in self._active_users():
            if self.usr[i]['members_cur_sbg'] in {1, 2, 3}:
                logger.debug(f"Marking a user as paid-invalid: {i}(sbg: {self.usr[i]['cur_sbg_num']})")
                self.usr[i]['cur_status'] = 'paid-invalid'
                self.usr[i]['wallet_reorg_refund'] = self.usr[i]['cur_mon_1st_calc']
                self.usr[i]['cur_mon_1st_calc'] = 0
                self.sys[self.period]['invalid_cnt'] += 1
                self.sys[self.period]['valid_remaining'] -= 1
        sd = self.sys[self.period]
        self.sys[self.period]['invalid_sf'] = sd['invalid_cnt'] * sd['cur_mon_1st_calc']

    def user_func_6(self):
        """
        User Quit Function
        :return:
        """
        quit_list = []
        for i in range(self._total):
            if self.usr[i]['cur_status'] == 'paid-invalid':
                if self.usr[i]['pri_role'] == 'low-morale':
                    if random.uniform(0, 1) > self.ev['low_morale_quit_prob']:
                        for j in range(self._total):
                            if self.usr[j]['cur_sbg_num'] == self.usr[i]['cur_sbg_num']:
                                self.usr[j]['sbg_reorg_cnt'] += 1
                        if self.usr[i]['sec_role'] == 'dependent':
                            quit_list.append(i)
                    else:
                        self.remove_usr(i, reason='low-morale')
                        self.sys[self.period]['quit_cnt'] += 1
                elif self.usr[i]['pri_role'] == 'unity':
                    for j in range(self._total):
                        if self.usr[j]['cur_sbg_num'] == self.usr[i]['cur_sbg_num']:
                            self.usr[j]['sbg_reorg_cnt'] += 1
        for i in quit_list:
            if self.usr[i]['sbg_reorg_cnt'] < 2:
                self.remove_usr(i, reason='low-morale-dependent')
                self.sys[self.period]['quit_cnt'] += 1

    def rsc(self):
        sd = self.sys[self.period]
        if self.period == 0:
            self.sys[self.period]['total_sf_period_one_claim'] = \
                sum([sd[k] for k in {'defection_sf', 'skip_sf', 'invalid_sf'}])
            self.sys[self.period]['individual_sf_period_one_claim'] = \
                self.sys[self.period]['total_sf_period_one_claim'] / sd['valid_remaining']

        self.sys[self.period]['cur_mon_total_sf'] = sd['skip_sf'] + sd['invalid_sf']
        self.sys[self.period]['cur_mon_individual_sf'] = \
            self.sys[self.period]['cur_mon_total_sf'] / sd['valid_remaining']

        credit_to_savings_account = self.cov_req / self._total
        for i in range(self._total):
            self.usr[i]['debit_to_savings_account'][self.period] = self.sys[self.period][
                    'individual_sf_period_one_claim' if self.period == 0 else 'cur_mon_individual_sf']
            if self.usr[i]['debit_to_savings_account'][self.period] > credit_to_savings_account \
                    and i in self._active_users():
                msg = f"Period: {self.period}, User{i}: Debit(" \
                      f"{self.usr[i]['debit_to_savings_account'][self.period]}) > " \
                      f"Credit({self.cov_req / self._total}) and the number of users is {len(self._active_users())}"
                raise ValueError(msg)

            self.usr[i]['cur_mon_balance'] += self.sys[self.period]['cur_mon_individual_sf']

    def _reorg_subgroups(self, left=3, right=2):
        invalid_users = [i for i in range(self._total) if self.usr[i]['cur_status'] == 'paid-invalid']
        ll = list(set([self.usr[i]['cur_sbg_num'] for i in invalid_users if self.usr[i]['members_cur_sbg'] == left]))
        rr = list(set([self.usr[i]['cur_sbg_num'] for i in invalid_users if self.usr[i]['members_cur_sbg'] == right]))
        if (ll and rr and left != right) or (len(ll) > 1 and left == right):
            # If left != right: Pick random ones from left & right groups
            # if left == right: Pick 1st one from left, and then random one from the remaining ones(left)
            sbg_num_left = ll[0]
            sbg_num_right = random.choice(rr if left != right else ll[1:])
            for i in invalid_users:
                if self.usr[i]['cur_sbg_num'] in {sbg_num_left, sbg_num_right}:
                    sbg_num = sbg_num_left if left > right else sbg_num_right
                    logger.debug(f"Reorganization of user {i}, {self.usr[i]['cur_sbg_num']} => {sbg_num}")
                    self.usr[i]['cur_sbg_num'] = sbg_num
                    self.usr[i]['members_cur_sbg'] = left + right
                    self.usr[i]['cur_status'] = 'valid'
                    self.usr[i]['reorged_cnt'] += 1
                    self.sys[self.period]['valid_remaining'] += 1
                    self.sys[self.period]['reorged_cnt'] += 1
            return True

    def _reorg_with_valid_users(self, left=3, right=2):
        invalid_users = [i for i in range(self._total) if self.usr[i]['cur_status'] == 'paid-invalid']
        ll = list(set([self.usr[i]['cur_sbg_num'] for i in invalid_users if self.usr[i]['members_cur_sbg'] == left]))
        rr = list(set([
            self.usr[i]['cur_sbg_num'] for i in self._active_users() if self.usr[i]['members_cur_sbg'] == right]))
        if ll and rr:
            # Pick random ones from left & right groups
            logger.debug(f"Reorganization of invalid({left}) & valid({right}) users")
            sbg_num_left = random.choice(ll)
            sbg_num_right = random.choice(rr)
            for i in range(self._total):
                if self.usr[i]['cur_sbg_num'] == sbg_num_left:
                    logger.debug(f"Reorganization of invalid user {i}, {self.usr[i]['cur_sbg_num']} => {sbg_num_right}")
                    self.usr[i]['cur_sbg_num'] = sbg_num_right
                    self.usr[i]['members_cur_sbg'] = left + right
                    self.usr[i]['cur_status'] = 'valid'
                    self.usr[i]['reorged_cnt'] += 1
                    self.sys[self.period]['valid_remaining'] += 1
                    self.sys[self.period]['reorged_cnt'] += 1
                elif self.usr[i]['cur_sbg_num'] == sbg_num_right:
                    logger.debug(f"Reorganization of valid user {i}, {self.usr[i]['cur_sbg_num']} => {sbg_num_right}")
                    self.usr[i]['members_cur_sbg'] = left + right
                    self.usr[i]['reorged_cnt'] += 1
            return True

    def sys_func_7(self):
        """
        Reorganization of Users
        Order:
                3 - 2, 3 - 3, 3 - 4
                2 - 3, 2 - 4, 2 - 5
                1 - 4, 1 - 5, 1 - 6
        """
        val_remain = copy.copy(self.sys[self.period]['valid_remaining'])
        for i in [3, 2, 1]:
            for j in range(3):
                while self._reorg_subgroups(i, 5 + j - i):
                    pass
        for i in [3, 2, 1]:
            for j in range(3):
                while self._reorg_with_valid_users(i, 5 + j - i):
                    pass
        # ALL paid-invalid users should be reorganized..
        invalid_users = [i for i in range(self._total) if self.usr[i]['cur_status'] == 'paid-invalid']
        if invalid_users:
            raise ValueError(F"Not all invalid users are reorganized - {len(invalid_users)}")
        sd = self.sys[self.period]
        if sd['reorged_cnt'] + sd['quit_cnt'] != sd['invalid_cnt']:
            raise ValueError("Invalid values after function7!")
        if val_remain + sd['reorged_cnt'] != sd['valid_remaining']:
            raise ValueError("Valid remaining mismatch after function7!")

    def sys_func_8(self):
        """"
        Determine Claims
        """
        claimed = random.uniform(0, 1) < self.ev['chance_of_claim']
        # TODO: REMOVE THIS!
        # claimed = False
        self.sys[self.period]['claimed'] = claimed
        if claimed:
            claimant = random.choice(self._active_users())
            logger.warning(f">>> Claim occurred by user{claimant} in period{self.period + 1}")
            for i in self._active_users():
                self.usr[claimant]['wallet_claim_award'] += self.usr[i]['cur_mon_balance']
                for m in range(self.bundling):
                    self.usr[claimant]['wallet_claim_award'] += self.usr[i]['prior_premiums'][m]
                    self.usr[i]['prior_premiums'][m] = 0
                self.usr[i]['cur_mon_balance'] = 0
        else:
            for i in range(self._total):
                self.usr[i]['cur_mon_premium'] = self.usr[i]['cur_mon_balance']
                self.usr[i]['cur_mon_balance'] = 0


if __name__ == '__main__':

    _ev = {
        'total_member_cnt': 60,
        'cov_req': 1000,
        'chance_of_claim': .40,
        'perc_honest_defectors': 0.2,
        'perc_low_morale': 0.1,
        'perc_independent': .70,
        'dependent_thres': 2,
        'low_morale_quit_prob': .1,
    }
    _pv = {
        'prem_inc_floor': .20,
        'ph_leave_floor': .05,
        'prem_inc_ceiling': .6,
        'ph_leave_ceiling': .15,
        'prem_inc_cum': .60,
        'ph_leave_cum': .20,
    }
    tps = TandaPaySimulatorV2(ev=_ev, pv=_pv)
    tps.start_simulation()
