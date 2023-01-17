from setuptools import find_packages, setup

setup(
    name="utils",
    version="0.1",
    description="",  # noqa
    author="",
    author_email="",
    install_requires=[
        "elasticsearch",
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
