"""PHI domain package.

Contains vault models, service interfaces, and demo adapters for HIPAA-ready workflows.
"""

from modules.phi.db import Base
from modules.phi.service import PHIService

__all__ = ["Base", "PHIService"]
