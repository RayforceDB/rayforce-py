from setuptools import setup, find_packages
from setuptools.dist import Distribution


class BinaryDistribution(Distribution):
    """Force platform-specific wheel."""
    def has_ext_modules(self):
        return True


setup(
    name='rayforce_py',
    version='1.3.0-beta',
    packages=find_packages(),
    package_data={
        'rayforce': ['*.so', '*.dylib', '*.pyi'],
        'rayforce.plugins': ['*.so', '*.dylib'],
    },
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.13',
    description='Python bindings for RayforceDB',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Karim',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: C',
    ],
    distclass=BinaryDistribution,
)
