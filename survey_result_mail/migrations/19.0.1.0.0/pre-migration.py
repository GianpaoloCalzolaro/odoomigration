# Copyright 2025 OCA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Pre-migration script for Odoo 19
    # Add any necessary pre-migration logic here
    pass
