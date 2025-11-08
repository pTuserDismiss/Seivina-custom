# Copyright © 2025 Novobi, LLC
# See LICENSE file for full copyright and licensing details.
{
    "name": "Oakworks Base",
    "version": "18.0.0.0",
    "category": "Hidden",
    "summary": "Base module for all Oakworks customizations",
    "description": """
        This is the base module that all Oakworks custom modules depend on.
        It provides common functionality and settings used across Oakworks modules.
    """,
    "author": "Novobi, LLC",
    "website": "https://novobi.com",
    "license": "OPL-1",
    "depends": ["base", "sale", "stock"],
    "data": [],
    "installable": True,
    "application": False,
    "auto_install": False,
    "sequence": 1,  # This ensures it loads first
    "post_init_hook": "_check_core_configs",
} 