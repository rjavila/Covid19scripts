from setuptools import setup, find_packages

setup(
    name = "covidplots",
    version = "0.0.1",
    description = "Plot the demise of the USA",
    packages = find_packages(),
    install_requires = ["pandas",
                        "python3-wget",
                        "bokeh>=2.3"]
    )
