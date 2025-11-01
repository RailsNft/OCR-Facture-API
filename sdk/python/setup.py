"""
Setup pour le package SDK Python OCR Facture API
"""

from setuptools import setup, find_packages
from pathlib import Path

# Lire le README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Lire les requirements si disponibles
requirements_file = Path(__file__).parent.parent.parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith("#") and not line.startswith("-")
        ]
    # Filtrer pour ne garder que les dépendances essentielles du SDK
    requirements = [
        req for req in requirements 
        if any(pkg in req.lower() for pkg in ["requests", "pydantic"])
    ]

# Si pas de requirements trouvés, utiliser les minimaux
if not requirements:
    requirements = ["requests>=2.32.0"]

setup(
    name="ocr-facture-api",
    version="2.0.0",
    description="SDK Python officiel pour l'API OCR Facture France - Extraction automatique de données de factures via OCR",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="OCR Facture API Team",
    author_email="support@ocr-facture-api.com",
    url="https://github.com/RailsNft/OCR-Facture-API",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=requirements,
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
        "Topic :: Scientific/Engineering :: Image Recognition",
    ],
    keywords="ocr invoice facture api sdk python extraction comptabilité accounting",
    project_urls={
        "Documentation": "https://github.com/RailsNft/OCR-Facture-API/tree/main/sdk/python",
        "Source": "https://github.com/RailsNft/OCR-Facture-API",
        "Tracker": "https://github.com/RailsNft/OCR-Facture-API/issues",
        "RapidAPI": "https://rapidapi.com/",
    },
    include_package_data=True,
    zip_safe=False,
)

