# Kafka–Databricks Sales Pipeline

**Real-Time Sales Analytics Pipeline:**  
Ingests live restaurant orders via a **Python Kafka Producer GUI**, processes them in **Databricks Delta Live Tables (DLT)** using a **multi-hop (Bronze–Silver–Gold)** architecture, and stores them in **Delta Lake**.  
The Gold layer powers a **Sales Dashboard** for near real-time business insights.

---

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Setup & Execution](#setup--execution)
  - [Step 1: Local Kafka Producer](#step-1-local-kafka-producer)
  - [Step 2: Databricks DLT Pipeline](#step-2-databricks-dlt-pipeline)
- [Dashboard & Insights](#dashboard--insights)
- [Verification Query](#verification-query)
- [Technologies Used](#technologies-used)
- [Author](#author)

---

## Overview

This repository demonstrates a **real-time restaurant sales analytics pipeline** for ingesting, transforming, and analyzing streaming data.

**Key Features:**
- Real-time ingestion through **Kafka Producer GUI**.
- Stream processing using **Databricks Delta Live Tables**.
- Clean Gold-layer table for dashboard-ready analytics.
- End-to-end architecture from **data entry → insights**.

---

## Architecture

```mermaid
graph TD
    A[Order Entry UI (Python)] -->|Sends Order JSON| B(Kafka Topic: restaurant-sales);
    B -->|Stream Ingestion| C{DLT Pipeline: Bronze Layer};
    C -->|Parse JSON & Store| D[Delta Table: sales_raw_delta];
    D -->|Stream Transformation| E{DLT Pipeline: Gold Layer};
    E -->|Flatten & Enrich| F[Delta Table: sales_transformed_mv];
    F -->|Query| G(Real-Time Sales Dashboard);
## Setup & Execution
<details> <summary><b> Prerequisites</b></summary>
Python 3.x
Kafka-Python Library
pip install kafka-python
Apache Kafka Cluster (with SSL certificates)(Used kafka service by Aiven)
ca.pem
service.cert
service.key
Databricks Workspace with Delta Live Tables (DLT) enabled
</details>

## Step 1: Local Kafka Producer
** 1.File Setup**
Ensure the following files are in the same folder:
->kafka_ui_producer.py
->ca-2.pem
->service-2.cert
->service-2.key
**2.Run the Producer Application**
->python kafka_ui_producer.py
**3.Generate Orders**
Use the Python GUI to enter orders.
Click SEND ORDER to publish JSON data to your Kafka topic (e.g., restaurant-sales).

## Step 2: Databricks DLT Pipeline
**1.Edit and Prepare Code**
->Open transformation.py
->Update with your Kafka server address and certificate content (for POC).
**2.Upload to Databricks Workspace**
->Navigate to Workspace → Upload File → transformation.py
**3.Create Delta Live Tables Pipeline**
->Go to Workflows → Delta Live Tables → Create Pipeline
->Source Code: path to your uploaded file
->Pipeline Mode: Continuous
->Target Schema: restaurant_sales
**4.Start the Pipeline**
->Click Start to begin continuous ingestion and transformation.
## Technologies Used
| Component         | Technology                    |
| ----------------- | ----------------------------- |
| Producer          | Python, Tkinter, Kafka-Python |
| Broker            | Apache Kafka                  |
| Stream Processing | Databricks Delta Live Tables  |
| Storage           | Delta Lake                    |
| Visualization     | Databricks SQL Dashboard      |
