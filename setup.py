from setuptools import setup, find_packages

setup(
    name="discord-music-bot",
    version="1.0.0",
    description="Discord Music Bot with YouTube and SoundCloud support",
    author="Discord Bot Developer",
    packages=find_packages(),
    install_requires=[
        "discord.py>=2.3.0",
        "yt-dlp>=2023.12.0",
        "PyNaCl>=1.5.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
)
