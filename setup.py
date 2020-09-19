from setuptools import setup, find_packages

setup(
    name = "covidplots",
    version = "0.0.1",
    description = "Plot the demise of the USA",
    packages = find_packages(),
    install_requires = ["pandas",
                        "geopandas",
                        "mapclassify",
                        "pywget",
                        "bokeh"]
    )
