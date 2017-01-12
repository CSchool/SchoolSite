import subprocess
import datetime
import csv
import io
from xml.etree import ElementTree

from CSchoolSite.settings import EJUDGE_CONTEST_ID, EJUDGE_USER_LOGIN
from CSchoolSite.settings import EJUDGE_USER_PASSWORD, EJUDGE_CONTESTS_CMD_PATH, EJUDGE_SESSION_TIMEOUT

from ejudge.session import get_session


STATUS_STRINGS = {
    "OK": "OK",
    "CE": "Compilation Error",
    "RT": "Run-Time Error",
    "TL": "Time-Limit Exceeded",
    "PE": "Presentation Error",
    "WA": "Wrong Answer",
    "CF": "Check Failed",
    "PT": "Partial Solution",
    "AC": "Accepted for Testing",
    "IG": "Ignored",
    "DQ": "Disqualified",
    "PD": "Pending",
    "ML": "Memory Limit Exceeded",
    "SE": "Security Violation",
    "SV": "Style Violation",
    "WT": "Time-Limit Exceeded",
    "PR": "Pending Review",
    "RJ": "Rejected",
    "SK": "Skipped",
    "SY": "Synchronization Error",
    "SM": "Summoned for defence",

    "RU": "Running...",
    "CD": "Waiting...",
    "CG": "Compiling...",
    "AV": "Waiting...",
    "EM": "Empty record"
}


def run_contests_cmd(action, *params):
    ssid = get_session()
    try:
        output = subprocess.check_output([
            EJUDGE_CONTESTS_CMD_PATH,
            str(EJUDGE_CONTEST_ID),
            action,
            "--session",
            ssid
        ] + list(map(str, params))).decode()
    except subprocess.CalledProcessError:
        return None
    return output


def get_run_info(run_id):
    """
    Return dict with run information:
        size - size in bytes
        compiler - compiler short name
        verdict - two letter verdict
        verbose_verdict - full English verdict name
        score_info - scoring info, usually failed test
        problem - problem name
        id - run id

    :param run_id: int or str - run id
    :return: dict with info or None on failure
    """
    scsv = run_contests_cmd("run-status", run_id)
    if scsv is None:
        return None

    f = io.StringIO(scsv)
    reader = csv.reader(f, delimiter=';')
    for row in reader:
        if int(row[0]) == int(run_id):
            size = int(row[3])
            problem = row[4]
            compiler = row[5]
            verdict = row[6]
            verbose_verdict = STATUS_STRINGS.get(row[6], row[6])
            try:
                score = int(row[7])
            except ValueError:
                score = None
            return {
                "size": size,
                "problem": problem,
                "compiler": compiler,
                "verdict": verdict,
                "verbose_verdict": verbose_verdict,
                "score": score,
                "id": int(run_id)
            }
    return None


def get_run_source(run_id):
    """
    Return run source code
    :param run_id: int or str - run id
    :return: str - source code
    """
    source = run_contests_cmd("dump-source", run_id)
    return source


def get_compiler_log(run_id):
    """
    Return compilation log for run
    :param run_id: int or str - run id
    :return: if compilation error occurred, log as str; None otherwise
    """
    xml = "\n".join(run_contests_cmd("dump-report", run_id).split("\n")[2:])
    f = io.StringIO(xml)
    tree = ElementTree.parse(f)
    if tree.getroot().get('compile-error', 'no') == "yes":
        el = tree.findall('compiler_output')
        if el:
            return el[0].text
    return None


def submit_run(problem_name, compiler, filename):
    """
    Submit run for checking
    :param problem_name: short problem name
    :param compiler: short compiler name
    :param filename: filename with source
    :return: int - run id
    """
    res = run_contests_cmd('submit-run', problem_name, compiler, filename)
    try:
        return int(res)
    except ValueError:
        return None


def get_available_compilers():
    """
    Get available compilers as dict: short name -> long name
    :return: dict or None on failure
    """
    scsv = run_contests_cmd("dump-languages")
    if scsv is None:
        return None

    f = io.StringIO(scsv)
    reader = csv.reader(f, delimiter=';')
    res = {}
    for row in reader:
        res[row[1]] = row[2]
    return res