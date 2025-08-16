from setuptools import setup, find_packages

setup(
    name="lox",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'lox=main:main',
        ],
    },
    python_requires='>=3.6',
)