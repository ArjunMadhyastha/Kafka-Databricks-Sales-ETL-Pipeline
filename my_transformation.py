from pyspark import pipelines as dp
from pyspark.sql.functions import *
from pyspark.sql.types import *
import sys
def read_file(filepath):
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Certificate file not found at {filepath}. Please upload it to your Databricks environment.")
        sys.exit(1)
ca_cert = read_file("/Volumes/workspace/default/...../ca.pem")
client_cert = read_file("/Volumes/workspace/default/...../service.cert")
client_key = read_file("/Volumes/workspace/default/...../service.key")

KAFKA_BOOTSTRAP_SERVERS = "kafka-.....-pipelineproject.f.aivencloud.com:....."
KAFKA_TOPIC = "Your Topic"

JSON_SCHEMA = StructType([
    StructField("order_id", IntegerType(), True),
    StructField("table_id", StringType(), True),
    StructField("customer_per_order", IntegerType(), True),
    StructField("payment_mode", StringType(), True),
    StructField("items", ArrayType(StructType([
        StructField("name", StringType(), True),
        StructField("quantity", IntegerType(), True),
        StructField("price", IntegerType(), True)
    ])), True),
    StructField("amount", IntegerType(), True),
    StructField("timestamp", LongType(), True)
])


MENU = [
    {"item": "Masala Dosa", "price": 70},
    {"item": "Idli", "price": 40},
    {"item": "Idli Vada", "price": 70},
    {"item": "Poori", "price": 50},
    {"item": "Chapati", "price": 50},
    {"item": "Plain Dosa", "price": 50},
    {"item": "Tea", "price": 10},
    {"item": "Coffee", "price": 15},
    {"item": "Cold Drink", "price": 20},
    {"item": "Lassi", "price": 25}
]


def get_transform_select_list():
    menu_item_cols = []
    for dish in MENU:
        item_name = dish['item']
        base_col_name = item_name.replace(' ', '_')
        
        quantity_expr = coalesce(
            aggregate(
                filter(col("items"), lambda x: x["name"] == item_name), lit(0), lambda acc, x: acc + x["quantity"]
            ), lit(0)
        ).alias(f"{base_col_name}_Q")
        
        price_expr = lit(dish['price']).alias(f"{base_col_name}_P")
        
        menu_item_cols.append(quantity_expr)
        menu_item_cols.append(price_expr)

    return [
        col("order_id"), col("table_id"), col("customer_per_order"), col("payment_mode"),
        *menu_item_cols,
        col("amount"),
        from_unixtime(col("timestamp")).alias("timestamp_standard")
    ]

@dp.table(
    name="kafka_raw_bronze",
    comment="Raw Kafka stream data with hardcoded SSL configuration for POC."
)
def kafka_raw_bronze():
    """Reads raw Kafka data using certificates defined directly in the script."""
    return (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", KAFKA_TOPIC)
        .option("kafka.security.protocol", "SSL") 
        .option("kafka.ssl.truststore.type", "PEM")
        .option("kafka.ssl.keystore.type", "PEM")
        .option("kafka.ssl.truststore.certificates", ca_cert)
        .option("kafka.ssl.keystore.certificate.chain", client_cert)
        .option("kafka.ssl.keystore.key", client_key)
        .option("kafka.ssl.endpoint.identification.algorithm", "")
        .option("failOnDataLoss", "false")
        .load()
    )

@dp.table(
    name="sales_raw_delta",
    comment="Parsed and cleaned data from Kafka, ready for transformation."
)
@dp.expect_or_drop("valid_json_parse", "order_id IS NOT NULL")
def sales_raw_delta():
    """Parses the raw Kafka value column into a structured format."""
    return (
        dp.read_stream("kafka_raw_bronze")
        .select(
            from_json(col("value").cast("string"), JSON_SCHEMA).alias("data")
        )
        .select("data.*")
    )



@dp.materialized_view(
    name="sales_transformed_mv",
    comment="Final flattened table with Q and P columns for each menu item, ready for analysis."
)
@dp.expect_or_drop("valid_order_id", "order_id IS NOT NULL")
def sales_transformed_mv():
    """Applies the flattening transformation logic."""
    
    df_from_raw = dp.read("sales_raw_delta")
    
    return df_from_raw.select(*get_transform_select_list())
