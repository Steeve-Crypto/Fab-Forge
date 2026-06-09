from setuptools import setup, find_packages

setup(
    name="fabforge",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["paho-mqtt", "click", "fastapi", "uvicorn", "asyncua", "torch", "scikit-learn"],
    entry_points={
        'console_scripts': [
            'grok-fab = fabforge.cli:cli',
        ],
    },
)
