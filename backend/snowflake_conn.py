import snowflake.connector
import os

# Set your file and table
CSV_FILE_PATH = "top_1000_us_patents.csv"
STAGE_NAME = "patent_stage"
TABLE_NAME = "patents_data"

# Snowflake connection details
conn = snowflake.connector.connect(
    user="RupamP",
    password="Rupam@1998",
    account="qxqznhd-qz34352",  # e.g. ab12345.us-east-1
    warehouse="COMPUTE_WH",
    database="PATENT_DB",
    schema="PUBLIC"
)
cursor = conn.cursor()

# ✅ Step 1: Create Stage if not exists
cursor.execute(f"CREATE OR REPLACE STAGE {STAGE_NAME};")

# ✅ Step 2: Upload file to stage
upload_query = f"PUT file://{CSV_FILE_PATH} @{STAGE_NAME} AUTO_COMPRESS=TRUE"
cursor.execute(upload_query)
print(" File uploaded to stage")

# ✅ Step 3: Load data into table
copy_query = f"""
COPY INTO {TABLE_NAME}
FROM @{STAGE_NAME}/{os.path.basename(CSV_FILE_PATH)}.gz
FILE_FORMAT = (TYPE = 'CSV' FIELD_OPTIONALLY_ENCLOSED_BY = '\"' SKIP_HEADER = 1)
ON_ERROR = 'CONTINUE';
"""
cursor.execute(copy_query)
print(" Data copied into table")

# Cleanup
cursor.close()
conn.close()
