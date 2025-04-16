from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="trucode",
    version="0.1.0",
    author="TruCode Developer",
    author_email="dev@trucode.example.com",
    description="A tool for analyzing Python code and suggesting improvements",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/trucode",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "trucode=trucode.main:main",
        ],
    },
)