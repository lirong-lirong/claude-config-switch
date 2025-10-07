'''
Author: lirong lirongleiyang@163.com
Date: 2025-10-07 17:45:01
LastEditors: lirong lirongleiyang@163.com
LastEditTime: 2025-10-07 18:30:13
FilePath: /claude-code-switch/setup.py
Description: 

Copyright (c) 2025 by lirong, All Rights Reserved. 
'''
from setuptools import setup, find_packages

setup(
    name="claude-code-switch",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer[all]",
        "rich",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "claude-switch=claude_switch.main:app",
        ],
    },
    author="lirong",
    author_email="lirongleiyang@163.com",
    description="A CLI tool for switching Claude Code API configurations",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
)