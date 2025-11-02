import tkinter as tk
import sqlite3
from os import remove, kill, path
from sys import executable as sys_executable
from sys import path as sys_path
from time import time
from signal import SIGTERM
from platform import system
from typing import List

from orchestration.command import CommandSpec
from orchestration.plans import RuntimePlan
from orchestration.process_manager import ProcessManager

PYTHON_EXECUTABLE = sys_executable or ""
if not PYTHON_EXECUTABLE:
    PYTHON_EXECUTABLE = ".venv/Scripts/python.exe" if system() == "Windows" else "macvenv/bin/python3"

####################################################################################
# [0] Getting System Config
####################################################################################
# Changing Path
sys_path.append("0-Settings/Program_Files/Misc/")
from read_config import run  # User Defined Function
program_settings = run()

####################################################################################
#[1] Setting Up application
####################################################################################
# -> Declaring the pairs to be traded
pair_list = program_settings["application_settings"]["pair_list"]

# -> Getting list of singular assets (Ex: BTC, ETH, USDT)
def sing_asset_list() -> List[str]:
    asset_pairs: List[str] = []
    for pair in pair_list:
        asset_pairs.append(pair.replace("USDT", ""))
    asset_pairs.append("USDT")
    return asset_pairs

asset_list = sing_asset_list()

# [A] Data Gathering Interval Settings
dg_settings = program_settings["application_settings"]["data_gathering"]

time_intervals = dg_settings["time_intervals"]  # Declaring time intervals

# [C] TRADING ENVIRONMENT (flag)
#     [0] LIVE TRADING
#     [1] DEMO TRADING
flag = program_settings["application_settings"]["trading_environment"]["flag"]

# [D] CREATING FOLDERS
sys_path.append("0-Run")
from Setup import start_1, start_2, start_3, start_4, start_5

start_1(pair_list)
start_2(pair_list)
start_3(pair_list)
start_4(pair_list)
start_5(pair_list)

# [1.4] Creating Python Files for gathering Account Balances -> 3-AccountBalance
from config_files.Account_Balance_files import Create_Trade_Balances
Create_Trade_Balances(trading_pair=pair_list)

# [1.5] Creates db file for strategies
sys_path.append("4-Strategies/Programs/")
from Strategy_2_Legacy import creating_db_file

strat_db_list = program_settings["application_settings"]["strategies"]
for strategy in strat_db_list:
    for pair in pair_list:
        creating_db_file(pair, "Binance", flag, db_name=strategy)

# [1.6] Legacy trade monitoring setup (no-op stubs)
from config_files.Trade_Monitoring_File_C import Create_Trade_Monitoring_Files
TMF_main = Create_Trade_Monitoring_Files(
    trading_pair=pair_list,
    exchange="Binance",
    flag=flag,
    chart_intervals=time_intervals,
)
TMF_main.create_asset_precision()  # Asset Precision
TMF_main.create_HIR_files()  # HIR

####################################################################################
# Helper functions for command construction
####################################################################################
def _script_command(script_path: str, *, name: str) -> CommandSpec:
    return CommandSpec(command=[PYTHON_EXECUTABLE, script_path], name=name)


def _core_commands() -> List[CommandSpec]:
    return [
        _script_command(
            "0-Run/RunTime_Tools/Restart_[Start(Main)].py",
            name="core:restart",
        ),
        _script_command(
            "ZZ-General_Functions/Programs/Delete_Files.py",
            name="core:cleanup",
        ),
    ]


def _file_monitoring_commands() -> List[CommandSpec]:
    scripts = [
        "Misc/Programs/FIle_Monitoring/File_Monitoring_1.py",
        "Misc/Programs/FIle_Monitoring/File_Monitoring_2.py",
        "Misc/Programs/FIle_Monitoring/File_Monitoring_5.py",
    ]
    return [
        _script_command(script, name=f"file-monitoring:{i+1}")
        for i, script in enumerate(scripts)
    ]


def _account_balance_commands() -> List[CommandSpec]:
    if flag == 1:
        return [
            _script_command(
                "3-AccountBalance/Programs/USDT/Paper_Trading_Account_Create_USDT.py",
                name="account_balance:USDT",
            )
        ]

    commands: List[CommandSpec] = []
    for asset in asset_list:
        script = f"3-AccountBalance/Programs/{asset}/Live_Account_Balance_Legacy_{asset}.py"
        commands.append(
            _script_command(script, name=f"account_balance:{asset}")
        )
    return commands


def orchestrated_command_sequence() -> List[CommandSpec]:
    plan = RuntimePlan(config=program_settings)
    groups = plan.command_groups()
    ordered = []
    ordered.extend(groups.get("data_gathering", []))
    ordered.extend(groups.get("technical_analysis", []))
    ordered.extend(groups.get("statistical_analysis", []))
    ordered.extend(groups.get("trade_monitoring", []))
    ordered.extend(groups.get("strategy", []))
    ordered.extend(groups.get("risk_management", []))

    commands: List[CommandSpec] = []
    for spec in ordered:
        argv = spec.argv
        if argv:
            argv = list(argv)
            if argv[0] == "python":
                argv[0] = PYTHON_EXECUTABLE
        commands.append(
            CommandSpec(
                command=argv,
                name=spec.name,
                env=dict(spec.env),
                cwd=spec.cwd,
                tags=dict(spec.tags),
            )
        )
    return commands


def all_command_specs() -> List[CommandSpec]:
    commands: List[CommandSpec] = []
    commands.extend(_core_commands())
    commands.extend(_account_balance_commands())
    commands.extend(orchestrated_command_sequence())
    commands.extend(_file_monitoring_commands())
    return commands

####################################################################################
# GUI helpers and runtime management
####################################################################################
process_manager = ProcessManager()

MAIN_TIME_FILE = "0-Run/RunTime_Tools/Data_Files/Main_program_timings.db"
MAIN_PROGRAM_TASKS = "0-Run/RunTime_Tools/Data_Files/Task_Manager.db"


def run_programs() -> None:
    commands = all_command_specs()
    if not commands:
        return

    process_manager.prune()
    if process_manager.processes:
        return

    connection = sqlite3.connect(MAIN_PROGRAM_TASKS)
    cursor = connection.cursor()

    launched = process_manager.launch(commands)
    for managed in launched:
        cursor.execute(
            "INSERT INTO Tasks (Process_Name, PID) VALUES (?, ?)",
            (managed.spec.describe(), str(managed.process.pid)),
        )
    connection.commit()
    connection.close()

    running_files.set("\n".join(proc.spec.describe() for proc in process_manager.processes))


def terminate_programs() -> None:
    if path.exists(MAIN_PROGRAM_TASKS):
        connection = sqlite3.connect(MAIN_PROGRAM_TASKS)
        cursor = connection.cursor()
        cursor.execute("Select * FROM Tasks")
        program_process_list = cursor.fetchall()
        connection.close()

        for _, pid in program_process_list:
            try:
                kill(int(pid), int(SIGTERM))
            except Exception:
                pass

        remove(MAIN_PROGRAM_TASKS)

    process_manager.terminate_all()
    process_manager.prune()
    running_files.set("")

####################################################################################
# Database utilities
####################################################################################
class create_database_files:
    # Initialising variables
    def __init__(self, file_name):
        self.file_name = file_name

    def program_timings(self):
        connection = sqlite3.connect(self.file_name)
        cursor = connection.cursor()
        command1 = """CREATE TABLE IF NOT EXISTS
        times(Start_Timestamp TEXT, Last_Updated TEXT)"""
        cursor.execute(command1)
        current_timestamp = round(time())
        cursor.execute(
            "INSERT INTO times (Start_Timestamp) VALUES (?)",
            (current_timestamp,),
        )
        connection.commit()
        connection.close()

    def live_programs(self):
        connection = sqlite3.connect(self.file_name)
        cursor = connection.cursor()
        command1 = """CREATE TABLE IF NOT EXISTS
        Tasks(Process_Name TEXT, PID TEXT)"""
        cursor.execute(command1)
        connection.commit()
        connection.close()

####################################################################################
# GUI initialisation
####################################################################################
root = tk.Tk()
root.title("Python Program Runner")

running_files = tk.StringVar()
running_files_label = tk.Label(root, textvariable=running_files)
running_files_label.pack()

run_button = tk.Button(root, text="Run Programs", command=run_programs)
run_button.pack()

terminate_button = tk.Button(root, text="Terminate Programs", command=terminate_programs)
terminate_button.pack()

####################################################################################
# Startup workflow
####################################################################################
def start_crypto_bot():
    db_start_names_list = [MAIN_TIME_FILE, MAIN_PROGRAM_TASKS]
    for file_name in db_start_names_list:
        if path.exists(file_name):
            remove(file_name)

    create_database_files(MAIN_TIME_FILE).program_timings()
    create_database_files(MAIN_PROGRAM_TASKS).live_programs()

    root.mainloop()

    if path.exists(MAIN_TIME_FILE):
        remove(MAIN_TIME_FILE)

start_crypto_bot()
