"""
Setup pour le package SDK Python OCR Facture API
"""

from setuptools import setup, find_packages
from pathlib import Path

# Lire le README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="ocr-facture-api",
    version="1.0.0",
    description="SDK Python officiel pour l'API OCR Facture France",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="OCR Facture API Team",
    author_email="support@ocr-facture-api.com",
    url="https://github.com/RailsNft/OCR-Facture-API",
    packages=find_packages(),
    install_requires=[
        "requests>=2.32.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial :: Accounting",
    ],
    keywords="ocr invoice facture api sdk python",
    project_urls={
        "Documentation": "https://github.com/RailsNft/OCR-Facture-API",
        "Source": "https://github.com/RailsNft/OCR-Facture-API",
        "Tracker": "https://github.com/RailsNft/OCR-Facture-API/issues",
    },
)

