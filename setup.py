import setuptools
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="fastapi_simple_security",
    version="0.1",
    packages=["fastapi_simple_security"],
    url="https://github.com/mrtolkien/fastapi_simple_security",
    license="MIT",
    author='Gary "Tolki" Mialaret',
    install_requires=["fastapi"],
    author_email="gary.mialaret+pypi@gmail.com",
    description="API key based security package for FastAPI, focused on simplicity of use",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
