from system_record import System_Record
from user_record import *

def sf4_invalidate_subgroups(sys_rec, user_list):
    
    invalid_indices = []

    for i in range(len(user_list)):
        user = user_list[i]
        if user.sbg_status != ValidityEnum.VALID:
            continue

        # 1. if members_cur_sbg = 1, 2, or 3
        if 1 <= user.members_cur_sbg <= 3:
            user.sbg_status = ValidityEnum.INVALID
            user.cur_status = CurrentStatusEnum.PAID_INVALID
            sys_rec.invalid_cnt += 1
            sys_rec.valid_remaining -= 1
            invalid_indices.append(i)

        # 2. set invalid_refund to first_premium_calc
        user.invalid_refund = sys_rec.first_premium_calc
        
        # 3. THIS STEP is incorrect and nolonger makes sense. User nolonger has this variable
        # user.first_premium_calc = 0

    # Calculate individual shortfall -- this step should happen because invalid_cnt has a setter which will automatically calculate this variable.

   # return invalid_indices
