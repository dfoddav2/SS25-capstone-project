# Datascience Capstone Project

This is the repository for the SS2025 datascience Capstone Project course assignment of Informatics BSc at IMC Krems.

This README purely serves as a guide on how to run the code and what is the general structure of the project like. To see the actual interpretation of the results see the [report](./report/REPORT.pdf).

## Get started

Preferably use a `.venv` and install the requirements via:

```bash
pip install -r requirements.txt
```

The scraper itself has separate requirements which you can separately install via the requirements file in its directory. To find out more about the scraper you may visit its [README.md](./scraper/README.md).

## Structure

The parts of the project have been organized into subdirectories based on their functionality:

```plaintext
CAPSTONE-PROJECT/
├── .gitignore
├── README.md
├── requirements.txt  (General Requirements for Notebooks)
├── all_car_details.parquet  (Initial scraped raw data)
├── all_car_details_cleaned.parquet  (Initial cleaned data)
├── all_car_details_harshly_cleaned.parquet  (Harshly cleaned dataset)
├── analysis/  (EDA and Data Cleaning notebooks)
├── prediction/  (One notebook for each prediction model)
├── report/  (Everything related to documentation)
|   ├── images/  (The exported images used in the report)
|   ├── Final Presentation.pdf
|   └── REPORT.pdf  (Main long format report)
└── scraper/  (Scraper code and requirements)
    ├── README.md
    ├── requirements.txt
    └── main.py
```

## Datasource and metadata

All car data was scraped from: [Autoscout24](https://www.autoscout24.com/) one of Europe's most prominent used car marketplace.

Time of scraping: 03/04/2025 - 21:00 - 08/04/2025
