import numpy as np
from scipy.stats import norm

from enum import Enum

class TestTypeEnum(Enum):
    TWOTAILED = 0
    GREATER = 1
    LESS = 2

def perform_hypothesis_test(mean, std_dev, sample_size, null_value, test_type):
    """
    Perform a hypothesis test for the given mean, standard deviation, sample size, null value, and test type.

    Parameters:
    - mean: The sample mean
    - std_dev: The sample standard deviation
    - sample_size: The size of the sample
    - null_value: The value under the null hypothesis
    - test_type: Type of test (TWOTAILED, GREATER, LESS from TestTypeEnum)

    Returns:
    - p_value: The p-value of the test
    """
    denom = (std_dev / np.sqrt(sample_size))
    # if we have such a small value on the bottom
    if denom == 0:
        return 0.0

    # Calculate the Z-score
    z_score = (mean - null_value) / denom

    # Calculate the p-value based on the test type
    if test_type == TestTypeEnum.TWOTAILED:
        p_value = 2 * (1 - norm.cdf(abs(z_score)))
    elif test_type == TestTypeEnum.GREATER:
        p_value = 1 - norm.cdf(z_score)
    elif test_type == TestTypeEnum.LESS:
        p_value = norm.cdf(z_score)

    return p_value

