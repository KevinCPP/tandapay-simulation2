from enum import Enum
from stats.hypothesis_test import TestTypeEnum
from stats.statistics_attributes import statistics_attributes

class OutcomeEnum(Enum):
    """
    Can be a win, loss, or draw
    """
    WIN = 0
    LOSS = 1
    DRAW = 2

class Other_Variables:
    """
    Stores a collection of other variables that are used for simulation runs,
    but not in the actual simulation itself. Includes things like sample size,
    trial sample size, trial count, ...
    """
    def __init__(self):
        # simulation runs
        self.sample_size = 1            # number of times to run the simulation

        # statistics
        self.trial_sample_size = 100    # number of times to run the simulation for each trial
        self.trial_count = 30           # number of trials to run the simulation for

        self.alpha = 0.05               # alpha value to be used for confidence intervals & hypothesis testing
        
        # searching
        self._test_type = TestTypeEnum.TWOTAILED
        self._test_outcome = "num_wins" 
        self.value_to_test = 0.500
        self.selected_graph = "num_wins"
        
        # settings path
        self.settings_path = "config/settings.ini"
        
        # validator
        self.validator_repeats = 10         # how many times will validator repeat to get a mean/std. dev?
        self.validator_num_samples = 200    # how many samples will validator use?
        self.validator_sample_size = 200    # how many runs per sample?
        self.maxsd = 5                      # max standard deviation away from defaults that the min/max allowable values are allowed to be

    @property
    def test_type(self):
        return self._test_type

    @test_type.setter
    def test_type(self, value):
        if isinstance(value, TestTypeEnum):
            self._test_type = value
        else:
            self._test_type = TestTypeEnum[value]

    @property
    def test_outcome(self):
        return self._test_outcome

    @test_outcome.setter
    def test_outcome(self, value):
        if not isinstance(value, str):
            raise TypeError("Attempting to pass non-string value to test_outcome. (attributes must be strings)")
        if value not in statistics_attributes:
            raise ValueError("Attempting to pass invalid attribute string to test_outcome.")

        self._test_outcome = value
