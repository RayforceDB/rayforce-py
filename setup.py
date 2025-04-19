from setuptools import setup


setup(
    name="raypy",
    version="0.1.0",
    description="Python library for RayforceDB",
    author="Karim",
    author_email="",
    url="https://github.com/singaraiona/raypy",
    packages=["raypy"],
    package_data={
        "raypy": ["*.so", "*.dylib", "*.dll", "*.py", "*.i"],
    },
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: C",
        "Topic :: Database",
    ],
)
