import ui
import time
import datetime

from simulation.simulation import *
from simulation.environment_variables import Environment_Variables
from simulation.pricing_variables import Pricing_Variables
from simulation.other_variables import *
from stats.statistics_runner import Statistics_Runner
from validation.validator import Validator
from stats.searching import Searching
from util.ini_handler import INI_Handler
from util.results_db import Results_DB


class Main:
    def __init__(self):
        self.uic = ui.UI_Context()
        self.version = "v3.3.0"
        self.ini_handler = INI_Handler("config/settings.ini")
        
        # read config file
        self.uic.ev_obj = self.ini_handler.read_environment_variables()
        self.uic.pv_obj = self.ini_handler.read_pricing_variables()
        self.uic.ov_obj = self.ini_handler.read_other_variables()
        
        # debugging validator
#        results = []
#        for i in range(10):
#            validator = Validator(self.uic.ov_obj, .23)
#            results.append(validator.validate())
#
#        print(f"validator results: {results}")

        # set callbacks
        self.uic.run_intensive_searching = self.run_intensive_searching_callback
        self.uic.run_simulation = self.run_simulation_callback
        self.uic.run_statistics = self.run_statistics_callback
        self.uic.run_searching = self.run_searching_callback
        self.uic.save_settings = self.save_settings_callback
        self.uic.run_validate = self.run_validate_callback
        self.uic.run_debug = self.run_debug_callback
        self.uic.history = self.run_history_callback
        self.uic.about = self.run_about_callback

        self.uic.history_db_obj = Results_DB()
        
        ui.initialize(self.uic)


    def run_simulation_callback(self) -> str:
        results_aggregator = exec_simulation_multiple(self.uic.ev_obj, self.uic.pv_obj, self.uic.ov_obj.sample_size)
        self.uic.history_db_obj.add_result("Simulation Run", self.version, results_aggregator.get_string())
        return results_aggregator

    def run_statistics_callback(self):
        statistics_runner = Statistics_Runner(self.uic.ev_obj, self.uic.pv_obj, self.uic.ov_obj)
        result_str = statistics_runner.get_string()
        self.uic.history_db_obj.add_result("Statistics Run", self.version, result_str)
        return statistics_runner.get_string(), statistics_runner.statistics_aggregator

    def run_searching_callback(self, attribute, target_percent, outcome, min_value, max_value, steps, order):
        searching = Searching(self.uic.ev_obj, self.uic.pv_obj, self.uic.ov_obj)
        searching_data = searching.perform_full_search(attribute, target_percent, outcome, min_value, max_value, steps, order)
        self.uic.history_db_obj.add_result("Searching Run", self.version, searching_data.results_str)
        return searching_data

    def run_intensive_searching_callback(self, prog_callback=None):
        searching = Searching(self.uic.ev_obj, self.uic.pv_obj, self.uic.ov_obj)
        searching_data = searching.perform_intensive_search_assigned_defectors(0.0, 1.0, 20, prog_callback)
        return searching_data

    def run_validate_callback(self, perc_honest_defectors, progress_bar_callback=None):
        validator_runs = []
        total_progress = 0.0
        def single_run_progress_callback(progress: float):
            progress_bar_callback(total_progress + (progress / self.uic.ov_obj.validator_repeats))

        for i in range(self.uic.ov_obj.validator_repeats):
            validator = Validator(self.uic.ov_obj, perc_honest_defectors, single_run_progress_callback)
            validator_runs.append(validator.validate())
            total_progress = (i+1) / self.uic.ov_obj.validator_repeats

        return validator_runs

    def run_debug_callback(self):
        result_dict = exec_simulation_debug(self.uic.ev_obj, self.uic.pv_obj)
        return f"""
        Result: {result_dict['result']}
        Wrote user record to CSV: {result_dict['user_csv_path']}
        Wrote system record to CSV: {result_dict['sys_csv_path']}
        """

    def save_settings_callback(self):
        self.ini_handler.write_environment_variables(self.uic.ev_obj)
        self.ini_handler.write_pricing_variables(self.uic.pv_obj)
        self.ini_handler.write_other_variables(self.uic.ov_obj)

    def run_history_callback(self):
        return "temporarily unavailable"

    def run_about_callback(self):
        return "temporarily unavailable"


if __name__ == "__main__":
    app = Main()
