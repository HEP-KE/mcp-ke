#!/usr/bin/env python3
"""Setup script that auto-generates requirements and README"""
from setuptools import setup
from setuptools.command.build_py import build_py
import subprocess
import sys


class CustomBuildCommand(build_py):
    """Build command that runs generator scripts first"""
    def run(self):
        subprocess.run([sys.executable, "automation/generate_requirements.py"], check=True)
        subprocess.run([sys.executable, "automation/update_readme.py"], check=True)
        super().run()


setup(cmdclass={"build_py": CustomBuildCommand})
