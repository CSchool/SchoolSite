"""
Ejudge helper functions
They DO NOT interact with django in any way
If you want to be able get submission ids - store them in database
"""

from .run import get_compiler_log, get_run_info, get_run_source, submit_run