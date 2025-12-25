from setuptools import setup, find_packages

setup(
    name="sentinel",
    version="0.1.0",
    description="Multi-agent orchestration system for autonomous project management",
    author="Troy",
    author_email="troy@sentinel.local",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "python-dotenv>=1.0.0",
        "psycopg2-binary>=2.9.9",
        "sqlalchemy>=2.0.23",
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "notion-client>=2.2.1",
        "anthropic>=0.7.0",
        "click>=8.1.7",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "sentinel=src.cli.cli:main",
        ],
    },
)
