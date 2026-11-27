"""Public robotic bronchoscopy + linear EBUS registry demo (synthetic samples only).

Stateless and independent of the workbench database. Importing the workbench
package first makes the bounded registry packages importable.
"""

import app.registry_workbench  # noqa: F401  (puts packages/*/src on sys.path)
