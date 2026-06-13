from collections import Counter
from app.core.celery_app import celery_app
from app.db.database import SessionLocal
from app.db.models import Job, Transaction, JobSummary
from app.services.data_pipeline import clean_and_load_csv
from app.services.ai_service import categorize_transactions_batch, generate_narrative_summary

@celery_app.task(bind=True)
def process_transaction_file(self, job_id: int, file_path: str):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return f"Error: Job {job_id} not found."
        
        job.status = "processing"
        db.commit()

        # --- STEP 1: CLEANING ---
        print(f"Starting Data Cleaning for Job {job_id}...")
        clean_row_count = clean_and_load_csv(file_path, job_id, db)
        
        # --- STEP 2: CATEGORIZATION ---
        print(f"Starting LLM Categorization for Job {job_id}...")
        uncategorized = db.query(Transaction).filter(
            Transaction.job_id == job_id, Transaction.category == 'Uncategorised'
        ).all()
        
        if uncategorized:
            batch_data = [{"id": txn.id, "merchant": txn.merchant, "amount": txn.amount} for txn in uncategorized]
            category_mapping, raw_response = categorize_transactions_batch(batch_data)
            
            for txn in uncategorized:
                if category_mapping and str(txn.id) in category_mapping:
                    txn.category = category_mapping[str(txn.id)]
                    txn.llm_category = category_mapping[str(txn.id)]
                txn.llm_failed = False if (category_mapping and str(txn.id) in category_mapping) else True
            db.commit()

        # --- STEP 3: NARRATIVE SUMMARY ---
        print(f"Generating Final Summary for Job {job_id}...")
        all_txns = db.query(Transaction).filter(Transaction.job_id == job_id).all()
        
        # Exact Python Math
        total_inr = sum(t.amount for t in all_txns if t.currency == 'INR' and t.amount)
        total_usd = sum(t.amount for t in all_txns if t.currency == 'USD' and t.amount)
        anomaly_count = sum(1 for t in all_txns if t.is_anomaly)
        
        # Find Top 3 Merchants
        merchants = [t.merchant for t in all_txns if t.merchant]
        top_merchants = [m[0] for m in Counter(merchants).most_common(3)]

        stats = {
            "total_spend_inr": round(total_inr, 2),
            "total_spend_usd": round(total_usd, 2),
            "top_merchants": top_merchants,
            "anomaly_count": anomaly_count
        }

        # Call Gemini for the narrative
        llm_summary = generate_narrative_summary(stats)

        # Save to Database
        summary_record = JobSummary(
            job_id=job_id,
            total_spend_inr=stats["total_spend_inr"],
            total_spend_usd=stats["total_spend_usd"],
            top_merchants=stats["top_merchants"],
            anomaly_count=stats["anomaly_count"],
            narrative=llm_summary.get("narrative", "Summary generated without narrative.") if llm_summary else "Failed to generate LLM summary.",
            risk_level=llm_summary.get("risk_level", "unknown") if llm_summary else "unknown"
        )
        db.add(summary_record)

        # --- FINAL COMMIT ---
        job.row_count_clean = clean_row_count
        job.status = "completed"
        db.commit()
        
        return f"Job {job_id} processed fully. Summary generated."
        
    except Exception as e:
        db.rollback()
        if job:
            job.status = "failed"
            job.error_message = str(e)
            db.commit()
        return f"Job {job_id} failed: {str(e)}"
    finally:
        db.close()