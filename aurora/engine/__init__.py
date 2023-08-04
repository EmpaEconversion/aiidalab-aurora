
from aiida.manage.configuration import load_profile

from .submit import submit_experiment

__all__ = [
    'submit_experiment',
]

load_profile()
