from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="discord-music-bot",
    version="2.0.0",
    author="7r6t",
    author_email="",
    description="بوت Discord للموسيقى مع حلول محسنة لمشكلة Rate Limiting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/7r6t/Discord_song_bot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Chat",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docker": [
            "docker>=5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "discord-music-bot=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.yml", "*.yaml"],
    },
    keywords=[
        "discord",
        "bot",
        "music",
        "youtube",
        "audio",
        "voice",
        "arabic",
        "rate-limiting",
        "docker",
        "render",
    ],
    project_urls={
        "Bug Reports": "https://github.com/7r6t/Discord_song_bot/issues",
        "Source": "https://github.com/7r6t/Discord_song_bot",
        "Documentation": "https://github.com/7r6t/Discord_song_bot#readme",
        "Discord": "https://discord.gg/",
    },
) 