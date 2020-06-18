"""
Extension for managing score projects at the commandline.
"""
from .ManageBuildTargetScript import ManageBuildTargetScript
from .ManageMaterialScript import ManageMaterialScript
from .ManageScoreScript import ManageScoreScript
from .ManageSegmentScript import ManageSegmentScript
from .ScorePackageScript import ScorePackageScript
from ._version import __version__, __version_info__
from .get_text_editor import get_text_editor

__all__ = [
    "__version__",
    "__version_info__",
    "get_text_editor",
    "ManageBuildTargetScript",
    "ManageMaterialScript",
    "ManageScoreScript",
    "ManageSegmentScript",
    "ScorePackageScript",
]
