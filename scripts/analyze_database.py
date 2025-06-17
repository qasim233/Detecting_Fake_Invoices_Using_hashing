import json
import pickle
from collections import Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_hash_database(db_path="legitimate_invoice_hashes.pkl"):
    """Analyze the hash database for insights"""
    
    try:
        # Load the database
        with open(db_path, 'rb') as f:
            db_data = pickle.load(f)
        
        legitimate_hashes = db_data['legitimate_hashes']
        invoice_metadata = db_data['invoice_metadata']
        
        logger.info("=== Hash Database Analysis ===")
        logger.info(f"Total legitimate invoice hashes: {len(legitimate_hashes)}")
        logger.info(f"Metadata entries: {len(invoice_metadata)}")
        
        # Analyze by split
        split_counter = Counter()
        source_counter = Counter()
        
        for hash_val, metadata in invoice_metadata.items():
            split_counter[metadata.get('split', 'unknown')] += 1
            source_counter[metadata.get('source', 'unknown')] += 1
        
        logger.info("\n=== Distribution by Split ===")
        for split, count in split_counter.items():
            logger.info(f"  {split}: {count} invoices")
        
        logger.info("\n=== Distribution by Source ===")
        for source, count in source_counter.items():
            logger.info(f"  {source}: {count} invoices")
        
        # Sample hash analysis
        logger.info("\n=== Sample Hashes ===")
        sample_hashes = list(legitimate_hashes)[:10]
        for i, hash_val in enumerate(sample_hashes, 1):
            logger.info(f"  {i}. {hash_val}")
        
        # Hash length analysis
        if legitimate_hashes:
            hash_lengths = [len(h) for h in legitimate_hashes]
            logger.info(f"\n=== Hash Statistics ===")
            logger.info(f"  Hash length: {hash_lengths[0]} characters (SHA256)")
            logger.info(f"  All hashes same length: {len(set(hash_lengths)) == 1}")
        
        # Check for duplicates (shouldn't be any in a set, but good to verify)
        logger.info(f"  Unique hashes: {len(legitimate_hashes)}")
        logger.info(f"  Duplicate check passed: {len(legitimate_hashes) == len(set(legitimate_hashes))}")
        
        # Save analysis report
        analysis_report = {
            "total_hashes": len(legitimate_hashes),
            "metadata_entries": len(invoice_metadata),
            "split_distribution": dict(split_counter),
            "source_distribution": dict(source_counter),
            "sample_hashes": sample_hashes,
            "hash_length": len(list(legitimate_hashes)[0]) if legitimate_hashes else 0
        }
        
        with open("database_analysis.json", "w") as f:
            json.dump(analysis_report, f, indent=2)
        
        logger.info(f"\nAnalysis report saved to database_analysis.json")
        
    except FileNotFoundError:
        logger.error(f"Database file {db_path} not found. Please run invoice_detector.py first.")
    except Exception as e:
        logger.error(f"Error analyzing database: {e}")

if __name__ == "__main__":
    analyze_hash_database()
