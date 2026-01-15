from setuptools import find_packages, setup
from setuptools.dist import Distribution


class BinaryDistribution(Distribution):
    def has_ext_modules(self):
        return True


setup(
    name="rayforce_py",
    version="0.5.0",
    packages=find_packages(),
    package_data={
        "rayforce": ["*.so", "*.dylib", "*.pyi", "bin/rayforce"],
        "rayforce.plugins": ["*.so", "*.dylib"],
    },
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.11",
    description="Python bindings for RayforceDB",
    long_description=open("README.md").read(),  # noqa: SIM115
    long_description_content_type="text/markdown",
    author="FalsePublicEnemy",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: C",
    ],
    entry_points={"console_scripts": ["rayforce=rayforce.cli:main"]},
    distclass=BinaryDistribution,
)
