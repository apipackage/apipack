#!/usr/bin/env python3
"""
APIpack - Automated API Package Generator
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text().strip().split("\n")

setup(
    name="apipack",
    version="0.1.0",
    description="Automated API package generator with LLM integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="APIpack Team",
    author_email="team@apipack.dev",
    url="https://github.com/apipack/apipack",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "apipack": [
            "templates/**/*",
            "config/**/*",
            "plugins/builtin/**/*",
        ]
    },
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
            "pre-commit",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
            "myst-parser",
        ],
        "all": [
            "docker",
            "kubernetes",
            "ansible",
        ]
    },
    entry_points={
        "console_scripts": [
            "apipack=apipack.cli:main",
        ],
        "apipack.plugins": [
            "rest=apipack.plugins.builtin.rest:RestPlugin",
            "grpc=apipack.plugins.builtin.grpc:GrpcPlugin",
            "graphql=apipack.plugins.builtin.graphql:GraphQLPlugin",
            "websocket=apipack.plugins.builtin.websocket:WebSocketPlugin",
            "cli=apipack.plugins.builtin.cli:CliPlugin",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    keywords="api generator llm mistral templates automation",
    project_urls={
        "Bug Reports": "https://github.com/apipack/apipack/issues",
        "Source": "https://github.com/apipack/apipack",
        "Documentation": "https://apipack.readthedocs.io/",
    },
)