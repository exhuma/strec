import os
from os.path import exists, join

from setuptools import find_packages, setup


def get_version():
    # type: () -> str
    """
    Retrieves the version information for this package.
    """
    filename = "strec/version.py"

    with open(filename) as fptr:
        # pylint: disable=invalid-name, exec-used
        obj = compile(fptr.read(), filename, "single")
        data = {}  # type: ignore
        exec(obj, data)
    return data["VERSION"]


with open("docs/README.rst") as fptr:
    LONG_DESCRIPTION = fptr.read()

if os.geteuid() == 0:
    CONF_TARGET = "/usr/share/strec/conf.d"
else:
    from os.path import expanduser, join

    CONF_TARGET = join(expanduser("~"), ".strec", "conf.d")

if not exists(CONF_TARGET):
    os.makedirs(CONF_TARGET)
    print("Created folder for config files: %r" % CONF_TARGET)

setup(
    name="strec",
    version=get_version(),
    description="Generic Coloriser",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/x-rst",
    author="Michel Albert",
    author_email="michel@albert.lu",
    license="GPL",
    install_requires=[
        "blessings",
        "blessings",
        "pyyaml",
        "typing_extensions",
    ],
    extras_require={
        "doc": [
            "furo",
            "sphinx",
        ],
        "test": [
            "pytest",
            "pytest-cov",
        ],
    },
    entry_points={"console_scripts": ["strec=strec.cli:main"]},
    data_files=[
        (
            CONF_TARGET,
            [
                join("strec/configs", _)
                for _ in os.listdir("strec/configs")
                if _[-1] != "~"
            ],
        )
    ],
    packages=find_packages(exclude=["tests.*", "tests"]),
    zip_safe=False,
)
