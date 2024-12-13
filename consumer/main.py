import os
import json
import logging
from kafka import KafkaConsumer
from google.cloud import bigquery

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# BigQuery schema
SCHEMA = [
    bigquery.SchemaField('id', 'STRING', mode='REQUIRED'),
    bigquery.SchemaField('post_type_id', 'STRING', mode='REQUIRED'),
    bigquery.SchemaField('accepted_answer_id', 'STRING', mode='NULLABLE'),
    bigquery.SchemaField('creation_date', 'TIMESTAMP', mode='REQUIRED'),
    bigquery.SchemaField('score', 'INTEGER', mode='REQUIRED'),
    bigquery.SchemaField('view_count', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('body', 'STRING', mode='REQUIRED'),
    bigquery.SchemaField('owner_user_id', 'STRING', mode='NULLABLE'),
    bigquery.SchemaField('last_editor_user_id', 'STRING', mode='NULLABLE'),
    bigquery.SchemaField('last_edit_date', 'TIMESTAMP', mode='NULLABLE'),
    bigquery.SchemaField('last_activity_date', 'TIMESTAMP', mode='NULLABLE'),
    bigquery.SchemaField('title', 'STRING', mode='NULLABLE'),
    bigquery.SchemaField('tags', 'STRING', mode='NULLABLE'),
    bigquery.SchemaField('answer_count', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('comment_count', 'INTEGER', mode='REQUIRED'),
    bigquery.SchemaField('content_license', 'STRING', mode='REQUIRED'),
    bigquery.SchemaField('parent_id', 'STRING', mode='NULLABLE')
]

def create_dataset_if_not_exists(client, dataset_id, project_id):
    """Create the dataset if it does not exist."""
    dataset_ref = bigquery.DatasetReference(project_id, dataset_id)
    try:
        client.get_dataset(dataset_ref)
        log.info(f"Dataset {dataset_id} already exists.")
    except Exception:
        log.info(f"Dataset {dataset_id} does not exist. Creating it.")
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        client.create_dataset(dataset)
        log.info(f"Created dataset {dataset_id}.")

def ensure_table_exists(client, dataset_id, table_id):
    """Ensure the BigQuery table exists."""
    table_ref = client.dataset(dataset_id).table(table_id)
    try:
        client.get_table(table_ref)
        log.info(f"Table {table_id} already exists.")
    except Exception:
        log.info(f"Table {table_id} does not exist. Creating it.")
        table = bigquery.Table(table_ref, schema=SCHEMA)
        client.create_table(table)
        log.info(f"Created table {table_id}.")

def insert_into_bigquery(client, dataset_id, table_id, record):
    """Insert a single record into BigQuery."""
    table_ref = client.dataset(dataset_id).table(table_id)
    rows_to_insert = [record]
    try:
        errors = client.insert_rows_json(table_ref, rows_to_insert)
        if errors:
            log.error(f"BigQuery insert errors: {errors}")
        else:
            log.info(f"Inserted record with ID {record.get('id')}")
    except Exception as e:
        log.error(f"Failed to insert into BigQuery: {e}")

def main():
    # Kafka configuration
    kafka_topic = "posts"
    kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    
    # BigQuery configuration
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./service-account.json"
    bigquery_client = bigquery.Client()
    dataset_id = "data_devops"
    table_id = "posts"
    
    # Ensure BigQuery dataset and table exist
    create_dataset_if_not_exists(bigquery_client, dataset_id, bigquery_client.project)
    ensure_table_exists(bigquery_client, dataset_id, table_id)

    # Kafka consumer setup
    consumer = KafkaConsumer(
        kafka_topic,
        bootstrap_servers=kafka_bootstrap_servers,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="post-consumer-group"
    )

    log.info("Kafka consumer started. Waiting for messages...")
    try:
        for message in consumer:
            post = message.value
            log.info(f"Consumed message: {post}")
            # Insert message into BigQuery
            insert_into_bigquery(bigquery_client, dataset_id, table_id, post)
    except KeyboardInterrupt:
        log.info("Consumer stopped.")
    finally:
        consumer.close()

if __name__ == "__main__":
    main()
