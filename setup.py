"""Setup.py for FastAPI-simple-Security."""
from setuptools import setup, find_packages
# List of requirements
requirements = []  # This could be retrieved from requirements.txt
# Package (minimal) configuration
setup(
    name="fastapi_simple_security",
    version="0.1.0",
    description="A FastAPI webservices for simple api_key security",
    packages=find_packages(),  # __init__.py folders search
    install_requires=requirements
)
