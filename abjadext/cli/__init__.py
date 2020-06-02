"""
Extension for managing score projects at the commandline.
"""
from .ManageBuildTargetScript import ManageBuildTargetScript
from .ManageMaterialScript import ManageMaterialScript
from .ManageScoreScript import ManageScoreScript
from .ManageSegmentScript import ManageSegmentScript
from .ScorePackageScript import ScorePackageScript
from ._version import __version__, __version_info__

__all__ = [
    "ManageBuildTargetScript",
    "ManageMaterialScript",
    "ManageScoreScript",
    "ManageSegmentScript",
    "ScorePackageScript",
    "__version__",
    "__version_info__",
]
