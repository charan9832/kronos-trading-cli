"""
Kronos Trading Agent - Setup Script
====================================
Install the Kronos CLI tool.
"""

from setuptools import setup, find_packages

setup(
    name="kronos-trading",
    version="1.0.0",
    description="Autonomous Trading Agent with RL + Kronos Oracle",
    author="Kronos Team",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "torch>=2.0.0",
        "rich>=13.0.0",
        "yfinance>=0.2.0",
    ],
    entry_points={
        'console_scripts': [
            'kronos=kronos:main',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
