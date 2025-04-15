# Patent Analytics Research Assistant

A comprehensive patent analytics research platform that provides backend APIs for processing patent PDFs, generating research reports using state-of-the-art language models, and creating interactive visualizations. The project integrates various services such as AWS S3, Pinecone, Snowflake, SerpAPI, and multiple LLM providers. A Streamlit-based frontend offers an interactive dashboard for users to process patents and view results.


##FrontEnd:http://34.30.2.49:8501    ##Backend:http://34.30.2.49:8000

##Demo Video:https://www.loom.com/share/db43dce9963b4a4b8b5ec485261d2294?sid=144b5971-1dc6-45cb-8995-2fbbd4fd2c11

#Code Lab:https://codelabs-preview.appspot.com/?file_id=1ldqqqhqLLGzsK-IgaUzhu5AldJs95aoBqzta1vpZ8kM#3

#Report Sample:[Research Report Sample.pdf](https://github.com/user-attachments/files/19745363/Research.Report.Sample.pdf)

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Setup and Installation](#setup-and-installation)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [Docker & Docker Compose](#docker--docker-compose)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Patent PDF Processing:**  
  Upload and process patent PDFs from AWS S3, perform OCR conversion, and generate semantic chunks.

- **Research Report Generation:**  
  Use advanced language models to generate detailed patent research reports.

- **Web Augmentation:**  
  Augment reports with related patents retrieved via SerpAPI.

- **Interactive Visualizations:**  
  Generate bar charts, heatmaps, box plots, and word clouds based on patent data.

- **Streamlit Dashboard:**  
  An intuitive frontend for interacting with the backend APIs and visualizing results.

- **Multi-Container Setup:**  
  Docker and Docker Compose support for seamless deployment of both backend and frontend services.

---

## Architecture
![image](https://github.com/user-attachments/assets/dbce9514-94c0-4bd4-a402-36a6b619c992)

The project consists of two main components:

1. **Backend (FastAPI):**
   - Processes patent PDFs and performs semantic analysis.
   - Integrates with Pinecone for embeddings and Snowflake for patent data.
   - Utilizes various LLM services for generating research reports.
   - Provides REST endpoints for processing, report generation, and visualizations.

2. **Frontend (Streamlit):**
   - Offers an interactive dashboard to select and process patents.
   - Displays generated reports and visualizations.
   - Communicates with the backend using REST API calls.

---

