import subprocess
import datetime

from CSchoolSite.settings import EJUDGE_CONTEST_ID, EJUDGE_USER_LOGIN
from CSchoolSite.settings import EJUDGE_USER_PASSWORD, EJUDGE_CONTESTS_CMD_PATH, EJUDGE_SESSION_TIMEOUT

cached_session_id = None
cached_session_time = None


def get_session():
    """
    Get ejudge session string
    :return: ejudge session string on success, None on failure
    """
    global cached_session_time, cached_session_id
    if cached_session_id is None or (datetime.datetime.now() - cached_session_time).seconds > EJUDGE_SESSION_TIMEOUT:
        try:
            cached_session_id = subprocess.check_output((
                EJUDGE_CONTESTS_CMD_PATH,
                str(EJUDGE_CONTEST_ID),
                "master-login",
                "STDOUT",
                EJUDGE_USER_LOGIN,
                EJUDGE_USER_PASSWORD
            ))
        except subprocess.CalledProcessError:
            return None
        cached_session_id = cached_session_id.decode().strip()
        cached_session_time = datetime.datetime.now()
    return cached_session_id