"""Setup remotepixel-tiler"""

from setuptools import setup, find_packages

# Runtime requirements.
inst_reqs = [
    "aws-sat-api~=2.0",
    "lambda-proxy~=5.0",
    "rio-color",
    "rio-tiler>=1.2.10",
    "rio_tiler_mosaic",
]

extra_reqs = {
    "test": ["mock", "pytest", "pytest-cov"],
    "dev": ["mock", "pytest", "pytest-cov", "pre-commit"],
}

setup(
    name="remotepixel-tiler",
    version="5.0.1",
    description=u"""""",
    long_description=u"",
    python_requires=">=3",
    classifiers=["Programming Language :: Python :: 3.6"],
    keywords="",
    author=u"Vincent Sarago",
    author_email="contact@remotepixel.ca",
    url="https://github.com/remotepixel/remotepixel-tiler",
    license="BSD",
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=inst_reqs,
    extras_require=extra_reqs,
    entry_points={
        "console_scripts": ["remotepixel-tiler = remotepixel_tiler.scripts.cli:cli"]
    },
)
