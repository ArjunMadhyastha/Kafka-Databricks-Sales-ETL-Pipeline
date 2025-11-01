# 🍽️ Kafka-Databricks-Sales-Pipeline

**Project Summary:**  
A real-time **sales analytics pipeline** that ingests live restaurant orders via a **Python GUI** → streams them to **Apache Kafka** → processes them with **Databricks Delta Live Tables (DLT)** → stores them in **Delta Lake** for powering a **real-time Sales Dashboard**.

---

## 🧩 Architecture Overview

The pipeline follows a **Bronze → Silver → Gold** architecture:

Order Entry UI (Python)
    ↓ Sends Order JSON
Kafka Topic: restaurant-sales
    ↓ Stream Ingestion
DLT Pipeline: Bronze Layer
    ↓ Parse JSON & Store
Delta Table: sales_raw_delta
    ↓ Stream Transformation
DLT Pipeline: Gold Layer
    ↓ Flatten & Enrich
Delta Table: sales_transformed_mv
    ↓ Query
Real-Time Sales Dashboard

---

## ⚙️ Setup & Execution

<details>
<summary><b>Prerequisites</b></summary>

- **Python 3.x**  
- **Kafka-Python Library:**  
  ```bash
  pip install kafka-python
  ```
- **Apache Kafka Cluster** with SSL certificates  
  *(Used Kafka service by Aiven or local Kafka setup)*  
  Required files:
  ```
  ca.pem
  service.cert
  service.key
  ```
- **Databricks Workspace** with Delta Live Tables (DLT) enabled
</details>

---

### 🧠 Step 1: Local Kafka Producer

**1️⃣ File Setup**  
Ensure the following files are in the same folder:
```
kafka_ui_producer.py  
ca.pem  
service.cert  
service.key  
```

**2️⃣ Run the Producer Application**
```bash
python kafka_ui_producer.py
```

**3️⃣ Generate Orders**  
Use the Python GUI to enter order data and click **SEND ORDER** to publish JSON to Kafka.

---

### 🧠 Step 2: Databricks DLT Pipeline

**1️⃣ Edit and Prepare Code**
- Open `transformation.py`
- Update your Kafka server address and certificate content (for POC simplicity).

**2️⃣ Upload to Databricks Workspace**
```
Workspace → Upload File → transformation.py
```

**3️⃣ Create Delta Live Tables Pipeline**
```
Workflows → Delta Live Tables → Create Pipeline
```

Set:
- **Source Code:** Path to your uploaded file  
- **Pipeline Mode:** Continuous  
- **Target Schema:** `restaurant_sales`

**4️⃣ Start the Pipeline**  
Click **Start** to begin continuous ingestion and transformation.

---

## 📈 Dashboard Visualization

The final Gold Layer table (`sales_transformed_mv`) supports the real-time Sales Dashboard:

![Real-Time Sales Dashboard for Restaurant Orders](assets/sales_dashboard.png)

| Metric | Source Column(s) | Business Insight |
|--------|------------------|------------------|
| Real-Time Revenue | amount | Instantaneous revenue tracking |
| Popular Items | `[ItemName]_Q` columns | Identify best-selling menu items |
| Payment Mode Split | payment_mode | Customer payment behavior trends |

---

## 🧪 Verification Query

Once the DLT pipeline is running, verify the output in Databricks SQL:

```sql
SELECT 
    timestamp_standard,
    payment_mode,
    amount,
    Masala_Dosa_Q,
    Coffee_Q
FROM restaurant_sales.sales_transformed_mv
ORDER BY timestamp_standard DESC;
```

---

## 🛠️ Technologies Used

| Component | Technology |
|------------|-------------|
| Message Queue | Apache Kafka |
| Stream Processing | Databricks Delta Live Tables |
| Storage Format | Delta Lake |
| Dashboard | Databricks SQL |
| GUI Producer | Python (Tkinter + kafka-python) |

---

## 📦 Folder Structure

```
├── kafka_ui_producer.py        # Python GUI Producer
├── transformation.py           # DLT transformation logic
├── assets/
│   └── sales_dashboard.png     # Dashboard visualization
├── README.md
```

---

## 👨‍💻 Author

Developed by **Arjun Madhyastha**  
Real-time analytics pipeline integrating Kafka and Databricks for continuous business intelligence.
