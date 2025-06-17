import hashlib
import json
import os
from datasets import load_dataset
from PIL import Image
import io
import pickle
from typing import Set, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InvoiceHashDetector:
    def __init__(self, hash_db_path = "legitimate_invoice_hashes.pkl"):
        """
        Initialize the Invoice Hash Detector
        
        Args:
            hash_db_path: Path to store/load the hash database
        """
        self.hash_db_path = hash_db_path
        self.legitimate_hashes: Set[str] = set()
        self.invoice_metadata: Dict[str, Dict] = {}
        
    def image_to_bytes(self, image):
        """Convert PIL Image to bytes for hashing"""
        if hasattr(image, 'save'):
            # PIL Image object
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
        else:
            # Already bytes
            return image
    
    def generate_sha256_hash(self, image):
        """Generate SHA256 hash for an invoice image"""
        try:
            image_bytes = self.image_to_bytes(image)
            sha256_hash = hashlib.sha256(image_bytes).hexdigest()
            return sha256_hash
        except Exception as e:
            logger.error(f"Error generating hash: {e}")
            return None
    
    def load_dataset_and_build_hash_db(self):
        """Load the Hugging Face dataset and build hash database"""
        logger.info("Loading invoices-donut-data-v1 dataset from Hugging Face...")
        
        try:
            # Load the dataset
            dataset = load_dataset("katanaml-org/invoices-donut-data-v1")
            logger.info(f"Dataset loaded successfully!")
            logger.info(f"Train samples: {len(dataset['train'])}")
            logger.info(f"Validation samples: {len(dataset['validation'])}")
            logger.info(f"Test samples: {len(dataset['test'])}")
            
            # Process all splits (train, validation, test) as legitimate invoices
            total_processed = 0

            for split_name in ['train', 'validation', 'test']:
                logger.info(f"Processing {split_name} split...")
                split_data = dataset[split_name]
                
                for idx in range(len(split_data)):
                    try:
                        # Get individual sample
                        sample = split_data[idx]
                        
                        # Extract image and ground_truth more robustly
                        if isinstance(sample, dict):
                            image = sample.get('image')
                            ground_truth = sample.get('ground_truth', {})
                        else:
                            # Handle case where sample might have attributes instead of dict keys
                            image = getattr(sample, 'image', None)
                            ground_truth = getattr(sample, 'ground_truth', {})
                        
                        if image is None:
                            logger.warning(f"No image found in sample {idx} of {split_name}")
                            continue
                        
                        # Generate hash for the invoice image
                        invoice_hash = self.generate_sha256_hash(image)
                        
                        if invoice_hash:
                            self.legitimate_hashes.add(invoice_hash)
                            
                            # Store metadata
                            self.invoice_metadata[invoice_hash] = {
                                'split': split_name,
                                'index': idx,
                                'ground_truth': ground_truth,
                                'source': 'donut-data-v1'
                            }
                            
                            total_processed += 1
                            
                            if total_processed % 50 == 0:
                                logger.info(f"Processed {total_processed} invoices...")
                                
                    except Exception as e:
                        logger.error(f"Error processing sample {idx} in {split_name}: {e}")
                        continue
            
            logger.info(f"Successfully processed {total_processed} legitimate invoices")
            logger.info(f"Unique hashes in database: {len(self.legitimate_hashes)}")
            
            # Save the hash database
            self.save_hash_database()
            
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            raise
    
    def save_hash_database(self):
        """Save the hash database to disk"""
        try:
            db_data = {
                'legitimate_hashes': self.legitimate_hashes,
                'invoice_metadata': self.invoice_metadata
            }
            
            with open(self.hash_db_path, 'wb') as f:
                pickle.dump(db_data, f)
                
            logger.info(f"Hash database saved to {self.hash_db_path}")
            
            # Also save as JSON for human readability
            json_path = self.hash_db_path.replace('.pkl', '.json')
            json_data = {
                'legitimate_hashes': list(self.legitimate_hashes),
                'total_hashes': len(self.legitimate_hashes),
                'metadata_sample': dict(list(self.invoice_metadata.items())[:5])  # Sample metadata
            }
            
            with open(json_path, 'w') as f:
                json.dump(json_data, f, indent=2)
                
            logger.info(f"Hash summary saved to {json_path}")
            
        except Exception as e:
            logger.error(f"Error saving hash database: {e}")
            raise
    
    def load_hash_database(self):
        """Load the hash database from disk"""
        try:
            if os.path.exists(self.hash_db_path):
                with open(self.hash_db_path, 'rb') as f:
                    db_data = pickle.load(f)
                    
                self.legitimate_hashes = db_data['legitimate_hashes']
                self.invoice_metadata = db_data['invoice_metadata']
                
                logger.info(f"Hash database loaded from {self.hash_db_path}")
                logger.info(f"Loaded {len(self.legitimate_hashes)} legitimate invoice hashes")
                return True
            else:
                logger.warning(f"Hash database file {self.hash_db_path} not found")
                return False
                
        except Exception as e:
            logger.error(f"Error loading hash database: {e}")
            return False
    
    def detect_fake_invoice(self, invoice_image):
        """
        Detect if an invoice is fake based on hash comparison
        
        Args:
            invoice_image: PIL Image or image bytes
            
        Returns:
            Dictionary with detection results
        """
        try:
            # Generate hash for the input invoice
            invoice_hash = self.generate_sha256_hash(invoice_image)
            
            if not invoice_hash:
                return {
                    'is_fake': True,
                    'confidence': 0.0,
                    'reason': 'Could not generate hash for the invoice',
                    'hash': None
                }
            
            # Check if hash exists in legitimate database
            is_legitimate = invoice_hash in self.legitimate_hashes
            
            result = {
                'is_fake': not is_legitimate,
                'confidence': 1.0 if is_legitimate else 0.9,  # High confidence for exact matches
                'hash': invoice_hash,
                'reason': 'Hash found in legitimate database' if is_legitimate else 'Hash not found in legitimate database'
            }
            
            # Add metadata if available
            if is_legitimate and invoice_hash in self.invoice_metadata:
                result['metadata'] = self.invoice_metadata[invoice_hash]
            
            return result
            
        except Exception as e:
            logger.error(f"Error during fake detection: {e}")
            return {
                'is_fake': True,
                'confidence': 0.0,
                'reason': f'Error during detection: {str(e)}',
                'hash': None
            }
    
    def get_database_stats(self):
        """Get statistics about the hash database"""
        return {
            'total_legitimate_hashes': len(self.legitimate_hashes),
            'database_file': self.hash_db_path,
            'database_exists': os.path.exists(self.hash_db_path),
            'sample_hashes': list(self.legitimate_hashes)[:5] if self.legitimate_hashes else []
        }

def main():
    """Main function to demonstrate the invoice detector"""
    logger.info("Starting Fake Invoice Detector using SHA256 Hashing")
    
    # Initialize detector
    detector = InvoiceHashDetector()
    
    # Try to load existing database
    if not detector.load_hash_database():
        logger.info("No existing hash database found. Building new database...")
        detector.load_dataset_and_build_hash_db()
    
    # Print database statistics
    stats = detector.get_database_stats()
    logger.info("Database Statistics:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")
    
    logger.info("Fake Invoice Detector is ready!")
    logger.info("You can now use detector.detect_fake_invoice(image) to check invoices")

if __name__ == "__main__":
    main()
