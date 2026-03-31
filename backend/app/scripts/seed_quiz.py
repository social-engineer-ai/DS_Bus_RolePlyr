"""Seed BADM 558 quiz independently (safe to run on existing DB).

Run with: python -m app.scripts.seed_quiz
"""

from uuid import UUID

from app.database import SessionLocal
from app.models.quiz import Quiz, QuizQuestion


COURSE_ID = UUID("55555555-5555-5555-5555-555555555555")
QUIZ_ID = UUID("aaaa0001-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


def seed_quiz():
    """Insert the BADM 558 quiz if it doesn't already exist."""
    print("Seeding BADM 558 quiz...")

    db = SessionLocal()
    try:
        existing = db.query(Quiz).filter(Quiz.id == QUIZ_ID).first()
        if existing:
            print("Quiz already exists. Skipping.")
            return

        quiz = Quiz(
            id=QUIZ_ID,
            course_id=COURSE_ID,
            title="BADM 558 \u2014 Big Data Infrastructure Quiz Prep",
            description="15 questions covering Kinesis Data Streams + Firehose, Glue ETL, and S3 + Athena. Answer any 5 questions (3 pts each, 15 pts total). Focus on WHY we use each service and KEY DECISIONS when configuring them.",
            max_attempts=10,
            is_active=True,
            show_answers_after_submit=True,
        )
        db.add(quiz)
        db.flush()

        questions = [
            # --- KINESIS DATA STREAMS + FIREHOSE (Q1-Q5) ---
            {
                "question_type": "short_answer",
                "question_text": "Q1. In the ShopStream lab, you sent the same order data to both Kinesis Data Streams and Firehose. The S3 outputs looked very different. Describe the key differences in what each pipeline produced and explain why.",
                "correct_answer": "Data Streams (via Lambda) produced one JSON file per order with enriched fields (processed_at, priority_flag) organized as processed/year/month/day/. Firehose produced batched NDJSON files of raw untransformed orders organized as year/month/day/hour/. The difference is because Data Streams gives a programmable consumer (Lambda) for custom logic, while Firehose is a managed delivery pipe that buffers and flushes with zero transformation.",
                "acceptable_answers": ["lambda", "enriched", "priority_flag", "batched", "NDJSON", "programmable consumer", "zero transformation", "custom processing", "one file per order", "buffered"],
                "points": 3,
                "order_index": 0,
            },
            {
                "question_type": "short_answer",
                "question_text": "Q2. A product manager says: \"Firehose is simpler and cheaper \u2014 why would we ever use Kinesis Data Streams?\" Give a specific business scenario where Kinesis Data Streams is necessary and Firehose alone would not work.",
                "correct_answer": "Firehose cannot run custom logic on individual records. If ShopStream needs to flag high-value orders (over $500) in real time so the fulfillment team can prioritize them immediately, Firehose cannot do this. You need Kinesis Data Streams with a Lambda consumer that inspects each order, applies business logic, enriches the record, and writes the result within sub-second latency.",
                "acceptable_answers": ["custom logic", "real-time", "lambda", "enrichment", "fraud detection", "business logic", "sub-second", "individual records", "cannot transform"],
                "points": 3,
                "order_index": 1,
            },
            {
                "question_type": "short_answer",
                "question_text": "Q3. In the lab, the Firehose buffer interval was set to 60 seconds. If you increased it to 300 seconds (5 minutes), how would the S3 output change? What is the trade-off?",
                "correct_answer": "With a 300-second buffer, Firehose would accumulate more records before flushing, producing fewer but larger files. The trade-off is latency vs. efficiency: longer buffers mean data takes longer to appear in S3 (up to 5 minutes delay) but you get fewer larger files that are more efficient for downstream tools like Athena. Shorter buffers give fresher data but create the small file problem.",
                "acceptable_answers": ["fewer", "larger files", "latency", "efficiency", "small file problem", "buffer", "delay", "batch", "trade-off"],
                "points": 3,
                "order_index": 2,
            },
            {
                "question_type": "short_answer",
                "question_text": "Q4. When you connected Lambda to the Kinesis Data Stream, you configured a \"starting position\" of \"Latest.\" What does this mean? What would happen if you chose \"Trim Horizon\" instead?",
                "correct_answer": "\"Latest\" means Lambda only processes records that arrive after the trigger is created, ignoring existing data. \"Trim Horizon\" means Lambda reads from the oldest available record in the stream (Kinesis retains data for 24 hours by default), processing all historical data. Trim Horizon is useful for reprocessing or catching up but can cause a burst of Lambda invocations.",
                "acceptable_answers": ["latest", "trim horizon", "oldest", "new events", "historical", "reprocess", "catch up", "backlog", "after the trigger", "24 hours"],
                "points": 3,
                "order_index": 3,
            },
            {
                "question_type": "short_answer",
                "question_text": "Q5. In the ShopStream lab, Lambda wrote one S3 object per order. If ShopStream scales to 1 million orders per day, why does this become a problem? Suggest an alternative approach.",
                "correct_answer": "One million individual S3 objects per day creates the \"small file problem.\" S3 charges per request (PUT, GET, LIST) and query engines like Athena perform poorly with millions of small files. Alternative: batch records in Lambda \u2014 accumulate records and write one file per batch (e.g., every 1000 records or 30 seconds). This is essentially what Firehose does automatically.",
                "acceptable_answers": ["small file", "batch", "firehose", "per request", "LIST operations", "overhead", "accumulate", "query performance", "cost"],
                "points": 3,
                "order_index": 4,
            },
            # --- GLUE ETL (Q6-Q10) ---
            {
                "question_type": "short_answer",
                "question_text": "Q6. In the Week 7 lab, the December CSV had a \"$\" prefix on the price column (e.g., \"$29.99\"). Could you fix this by simply editing the column type to DOUBLE in the Glue Data Catalog? Why or why not?",
                "correct_answer": "No. The Data Catalog stores metadata (column names, types, file locations) but does not change the actual data in S3. The string \"$29.99\" is physically in the CSV. Changing the catalog type to DOUBLE would cause Athena to fail with a parsing error or return NULL. You need ETL to strip the \"$\" and cast to a number \u2014 this is what the Glue Visual Editor SQL transform did with REGEXP_REPLACE. Metadata describes data; ETL transforms data.",
                "acceptable_answers": ["metadata", "does not change", "actual data", "ETL", "REGEXP_REPLACE", "parsing error", "NULL", "transform", "strip"],
                "points": 3,
                "order_index": 5,
            },
            {
                "question_type": "short_answer",
                "question_text": "Q7. You ran a Glue Crawler on the orders data and it could have created three separate tables (one per month) instead of one unified table. What setting prevents this, and why does it matter?",
                "correct_answer": "\"Create a single schema for each S3 path\" under Advanced Options / S3 Schema Grouping when configuring the Crawler. This merges all partitions into one table with a combined schema. Without it, the Crawler creates separate tables for each month, requiring UNION ALL queries instead of simple partitioned queries.",
                "acceptable_answers": ["single schema", "schema grouping", "merge", "unified table", "UNION ALL", "partitions", "combined schema", "advanced options"],
                "points": 3,
                "order_index": 6,
            },
            {
                "question_type": "short_answer",
                "question_text": "Q8. In the Week 7 lab, November CSV added a \"region\" column that October didn't have, and December renamed \"customer_id\" to \"cust_id.\" This is called schema evolution. Explain what problems this creates when querying across all three months in Athena.",
                "correct_answer": "Two problems: (1) The added region column: October rows return NULL for region \u2014 manageable, additive schema change. (2) The renamed customer_id to cust_id: CSV maps positionally so data lands correctly, but the Crawler sees two separate columns. October/November have customer_id populated but cust_id NULL; December has cust_id but customer_id NULL. Queries need COALESCE or ETL must standardize the column name.",
                "acceptable_answers": ["NULL", "region", "customer_id", "cust_id", "positionally", "COALESCE", "schema evolution", "renamed", "two columns", "additive"],
                "points": 3,
                "order_index": 7,
            },
            {
                "question_type": "short_answer",
                "question_text": "Q9. The Glue Visual Editor generated a PySpark script behind the scenes. Why might a data engineer choose to edit that generated script directly instead of continuing to use the visual interface?",
                "correct_answer": "The Visual Editor has limits. A data engineer would switch to the script for: complex conditional logic, calling external APIs, custom error handling, multi-path pipelines, ML feature engineering, or transformations that can't be expressed in a single SQL block. The generated script is also version-controllable in Git for change tracking, code review, and rollback. Teams often start with the visual editor for prototyping and graduate to scripts.",
                "acceptable_answers": ["complex logic", "conditional", "API", "Git", "version control", "error handling", "multi-path", "feature engineering", "limits", "prototyping"],
                "points": 3,
                "order_index": 8,
            },
            {
                "question_type": "short_answer",
                "question_text": "Q10. When you configured the Glue ETL job, you set the worker type to G.1X and requested 2 workers. Why does this matter, and what would you change if the dataset was 100x larger?",
                "correct_answer": "Glue workers are compute resources that cost money per second. G.1X is the smallest worker type (4 vCPUs, 16 GB). For the lab's tiny dataset, 2 workers is enough. For 100x larger, increase workers (e.g., 10-20) so Spark can parallelize across machines, and possibly upgrade to G.2X (8 vCPUs, 32 GB) for more memory. Glue also offers auto-scaling for variable workloads.",
                "acceptable_answers": ["workers", "cost", "parallelize", "G.1X", "G.2X", "Spark", "auto-scaling", "compute", "memory", "vCPU"],
                "points": 3,
                "order_index": 9,
            },
            # --- S3 + ATHENA (Q11-Q15) ---
            {
                "question_type": "short_answer",
                "question_text": "Q11. In the Week 6 lab, you ran the same query on the CSV table and the Parquet table. The query results were identical, but the data scanned was very different. Why does Parquet scan less data, and why does that matter for cost?",
                "correct_answer": "Parquet is columnar \u2014 it stores column values together, so Athena reads only needed columns and skips the rest. CSV is row-based \u2014 reading one column requires scanning all columns. Parquet also uses compression (Snappy). This matters because Athena charges $5/TB scanned, so less data scanned = lower cost. At scale, this means thousands of dollars in annual savings.",
                "acceptable_answers": ["columnar", "column", "skip", "row-based", "compression", "Snappy", "$5 per TB", "cost", "scan less"],
                "points": 3,
                "order_index": 10,
            },
            {
                "question_type": "short_answer",
                "question_text": "Q12. Query 3 in the basic lab (MIN, MAX, AVG on just the price column) showed the biggest gap between CSV and Parquet data scanned. Why did this specific query show the largest difference?",
                "correct_answer": "Query 3 touched only ONE column (price) out of 10 total. Parquet reads only the price column (~1/10th of data). CSV must scan all 10 columns for every row. Queries 1 and 2 used 2-4 columns, so Parquet still won but the gap was smaller. The fewer columns needed relative to total, the bigger Parquet's advantage \u2014 especially powerful for analytics on wide tables.",
                "acceptable_answers": ["one column", "price", "10 columns", "1/10", "all columns", "fewer columns", "wider", "advantage", "row by row"],
                "points": 3,
                "order_index": 11,
            },
            {
                "question_type": "short_answer",
                "question_text": "Q13. You built a three-tier folder structure: bronze, silver, and gold. Explain what each layer stores and why you would keep the raw CSV in bronze even after converting it to Parquet in silver.",
                "correct_answer": "Bronze: raw, as-received data in original format \u2014 never modified, source of truth. Silver: cleaned, typed, format-converted data (CSV to Parquet) for analytical queries. Gold: pre-computed aggregations and KPIs for dashboards. Keep raw CSV in bronze because: (1) if conversion has a bug, re-run from original; (2) business requirements change, original is always available; (3) auditing and compliance; (4) easier to diagnose schema/quality issues.",
                "acceptable_answers": ["bronze", "silver", "gold", "raw", "source of truth", "cleaned", "aggregation", "Parquet", "re-run", "audit", "compliance"],
                "points": 3,
                "order_index": 12,
            },
            {
                "question_type": "short_answer",
                "question_text": "Q14. The analytics team runs ad-hoc queries on the 50,000-row book catalog a few times per week. Why is Athena a better fit for this workload than setting up a traditional database like RDS?",
                "correct_answer": "Athena is serverless \u2014 no infrastructure to provision, manage, or pay for when idle. Pay only per query ($5/TB scanned), and with Parquet on 50K rows each query costs fractions of a cent. RDS would require a 24/7 running instance costing money every hour even when idle. For a few queries per week, you'd pay for a server sitting idle 99%+ of the time. Athena queries S3 directly with no loading or ETL needed.",
                "acceptable_answers": ["serverless", "idle", "pay per query", "$5/TB", "no infrastructure", "24/7", "running instance", "cost", "S3 directly"],
                "points": 3,
                "order_index": 13,
            },
            {
                "question_type": "short_answer",
                "question_text": "Q15. Your bookstore uploads a new catalog CSV every month. If the new file has a column added in the middle of the existing columns (not at the end), what problem does this cause when Athena queries the CSV table? Why doesn't this problem affect Parquet?",
                "correct_answer": "CSV maps columns positionally \u2014 Athena reads the 1st value as column 1, 2nd as column 2, etc. A column inserted in the middle shifts every subsequent column, mapping wrong data to wrong columns (prices in rating column, etc.) with no error message. Parquet stores column names inside the file and maps by name, not position, so reordering/adding columns doesn't cause misalignment. Parquet is inherently safer for schema evolution.",
                "acceptable_answers": ["positionally", "position", "shift", "wrong column", "by name", "column name", "schema evolution", "no error", "misalignment", "embedded"],
                "points": 3,
                "order_index": 14,
            },
        ]

        for q_data in questions:
            db.add(QuizQuestion(quiz_id=quiz.id, **q_data))

        db.commit()
        print(f"Created BADM 558 quiz with {len(questions)} questions.")
        print("Quiz ID:", QUIZ_ID)

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_quiz()
