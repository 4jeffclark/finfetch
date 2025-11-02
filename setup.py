"""
Setup script for FinFetch.
"""

from setuptools import setup, find_packages

setup(
    name="finfetch",
    version="0.1.0",
    description="Financial Data Collection, Aggregation and Processing Utilities",
    author="FinFetch Development Team",
    author_email="dev@finfetch.com",
    packages=["finfetch", "finfetch.analysis", "finfetch.config", "finfetch.core", "finfetch.processors", "finfetch.sources", "finfetch.utils"],
    package_dir={"finfetch": "src"},
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "structlog>=22.0.0",
    ],
    entry_points={
        "console_scripts": [
            "finfetch=finfetch.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)