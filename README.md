# LCA-Informed ANP-BOCR Decision Support Framework

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview
This repository contains the interactive Python-based decision support prototype developed for the paper: **"A Python-Based LCA-Informed ANP-BOCR Decision Support Framework for Cross-Sector Industrial Waste Management: Evidence from Metal Button Manufacturing."**

The framework integrates Life Cycle Assessment (LCA) environmental hotspot diagnosis with an Analytic Network Process (ANP) and Benefits, Opportunities, Costs, and Risks (BOCR) prioritization engine. It is designed as an interactive web application to help manufacturing practitioners and researchers evaluate and rank industrial waste management strategies (e.g., chemical stabilization, biological remediation, sludge valorization) across different sectoral scenarios.

## Features
* **Interactive Streamlit Dashboard:** Real-time, dynamic adjustment of BOCR global weights via an intuitive web interface.
* **Matrix-Based Priority Engine:** Uses the principal eigenvector method to calculate local priorities from pairwise comparison matrices.
* **Automated Consistency Checking:** Instantly calculates and reports the Consistency Ratio (CR) to validate mathematical rigor and expert judgments.
* **Cross-Sector Scenario Analysis:** Parameterized to evaluate strategic stability across Metal Button, Automotive, and Electronics manufacturing waste contexts.
* **Advanced Visualizations:** Includes cross-sector priority bar charts and stacked component contribution charts to illustrate why specific strategies dominate.
* **Publication-Ready Export:** One-click download of the complete Decision Matrix and Consistency Ratios as a multi-sheet Excel file.

## Installation

1. Clone this repository to your local machine:
   ```bash
   git clone [https://github.com/maulida-butar/anp-bocr-waste-management.git](https://github.com/maulida-butar/anp-bocr-waste-management.git)
   cd anp-bocr-waste-management
