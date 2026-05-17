"""
TRI-X: Triage-TiTrATE-XAI Framework for Emergency Decision Support

Package configuration for the TRI-X framework, which implements screening-first
risk governance logic (SRGL) for safe AI decision-making in critical systems.

Author: Chatchai Tritham
Supervisor: Chakkrit Snae Namahoot
Institution: Department of Computer Science and Information Technology, Faculty of Science, Naresuan University, Phitsanulok 65000, Thailand
"""

from setuptools import setup, find_packages
from pathlib import Path

# Grab the README content for PyPI
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
 long_desc = readme_path.read_text(encoding="utf-8")
else:
 long_desc = ""

setup(
 name="trix",
 version="1.0.0",
 author="Chatchai Tritham, Chakkrit Snae Namahoot",
 author_email="chatchait66@nu.ac.th, chakkrits@nu.ac.th",
 description="TRI-X: Triage-TiTrATE-XAI Framework for Emergency Decision Support",
 long_description=long_desc,
 long_description_content_type="text/markdown",
 url="https://github.com/ChatchaiTritham/TRI-X",
 package_dir={"": "src"},
 packages=find_packages(where="src"),
 classifiers=[
 "Development Status :: 4 - Beta",
 "Intended Audience :: Science/Research",
 "Intended Audience :: Healthcare Industry",
 "Topic :: Scientific/Engineering :: Artificial Intelligence",
 "Topic :: Scientific/Engineering :: Medical Science Apps.",
 "License :: OSI Approved :: MIT License",
 "Programming Language :: Python :: 3",
 "Programming Language :: Python :: 3.9",
 "Programming Language :: Python :: 3.10",
 "Programming Language :: Python :: 3.11",
 ],
 python_requires=">=3.9",
 install_requires=[
 "numpy>=1.21.0",
 "pandas>=1.3.0",
 "scikit-learn>=1.0.0",
 "matplotlib>=3.4.0",
 "seaborn>=0.11.0",
 "shap>=0.40.0",
 "lime>=0.2.0",
 "scipy>=1.7.0",
 "tqdm>=4.62.0",
 ],
 extras_require={
 "dev": [
 "pytest>=7.0.0",
 "pytest-cov>=3.0.0",
 "black>=22.0.0",
 "flake8>=4.0.0",
 "jupyter>=1.0.0",
 "jupyterlab>=3.0.0",
 "mypy>=0.910",
 ],
 "docs": [
 "sphinx>=4.0.0",
 "sphinx-rtd-theme>=1.0.0",
 ],
 },
 entry_points={
 "console_scripts": [
 "trix-demo=trix.cli:demo",
 "trix-validate=trix.cli:validate",
 ],
 },
)
