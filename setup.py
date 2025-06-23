from setuptools import setup, find_packages

setup(
    name="walter",
    version="0.1.0",
    description="Walter: CLI commands generator.",
    author="NoLilypad",
    packages=find_packages(),
    install_requires=[
        "annotated-types==0.7.0",
        "anyio==4.9.0",
        "certifi==2025.6.15",
        "charset-normalizer==3.4.2",
        "eval_type_backport==0.2.2",
        "h11==0.16.0",
        "httpcore==1.0.9",
        "httpx==0.28.1",
        "idna==3.10",
        "mistralai==1.8.2",
        "platformdirs==4.3.8",
        "pydantic==2.11.7",
        "pydantic_core==2.33.2",
        "python-dateutil==2.9.0.post0",
        "PyYAML==6.0.2",
        "requests==2.32.4",
        "six==1.17.0",
        "sniffio==1.3.1",
        "termcolor==3.1.0",
        "typing-inspection==0.4.1",
        "typing_extensions==4.14.0",
        "urllib3==2.4.0"
    ],
    entry_points={
        'console_scripts': [
            'walter=walter.__main__:main',
        ],
    },
    python_requires=">=3.8",
)
