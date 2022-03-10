from setuptools import setup, find_packages

setup(
    name = "covidplots",
    version = "0.1",
    description = "Plot the demise of the USA",
    packages = find_packages(),
    install_requires = ["pandas",
                        "requests",
                        "bokeh>=2.3"]
    )
