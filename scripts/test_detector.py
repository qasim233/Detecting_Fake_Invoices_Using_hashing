import os
import sys
from invoice_detector import InvoiceHashDetector
from datasets import load_dataset
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_detector():
    """Test the invoice detector with sample data"""
    logger.info("Testing Fake Invoice Detector...")
    
    # Initialize detector
    detector = InvoiceHashDetector()
    
    # Load the hash database
    if not detector.load_hash_database():
        logger.error("Hash database not found. Please run invoice_detector.py first.")
        return
    
    try:
        # Load a small sample from the dataset for testing
        logger.info("Loading test samples...")
        dataset = load_dataset("katanaml-org/invoices-donut-data-v1")
        
        # Get test split
        test_split = dataset['test']
        num_samples = min(5, len(test_split))
        
        logger.info("Testing with legitimate invoices (should be detected as legitimate):")
        
        for idx in range(num_samples):
            try:
                # Access individual sample correctly
                sample = test_split[idx]
                
                # Extract image from sample (we know it's a dict with 'image' key)
                image = sample['image']
                ground_truth = sample['ground_truth']
                
                # Test detection
                result = detector.detect_fake_invoice(image)
                
                status = "LEGITIMATE" if not result['is_fake'] else "FAKE"
                logger.info(f"Test {idx + 1}: {status} (Confidence: {result['confidence']:.2f})")
                logger.info(f"  Hash: {result['hash'][:16] if result['hash'] else 'None'}...")
                logger.info(f"  Reason: {result['reason']}")
                logger.info(f"  Image size: {image.size}")
                
                if 'metadata' in result:
                    logger.info(f"  Source: {result['metadata']['source']}")
                
                print("-" * 50)
                
            except Exception as e:
                logger.error(f"Error processing sample {idx}: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                continue
        
        # Test with a synthetic "fake" invoice (create a simple test image)
        logger.info("Testing with a synthetic fake invoice:")
        
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple fake invoice image
        fake_image = Image.new('RGB', (400, 600), color='white')
        draw = ImageDraw.Draw(fake_image)
        
        # Try to use a default font, fallback to basic if not available
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        draw.text((50, 50), "FAKE INVOICE", fill='black', font=font)
        draw.text((50, 100), "This is not a real invoice", fill='black', font=font)
        draw.text((50, 150), "Amount: $999.99", fill='black', font=font)
        draw.text((50, 200), "Company: Fake Corp", fill='black', font=font)
        draw.text((50, 250), "Date: 2024-01-01", fill='black', font=font)
        
        fake_result = detector.detect_fake_invoice(fake_image)
        
        status = "LEGITIMATE" if not fake_result['is_fake'] else "FAKE"
        logger.info(f"Fake Invoice Test: {status} (Confidence: {fake_result['confidence']:.2f})")
        logger.info(f"  Hash: {fake_result['hash'][:16] if fake_result['hash'] else 'None'}...")
        logger.info(f"  Reason: {fake_result['reason']}")
        logger.info(f"  Image size: {fake_image.size}")
        
        # Test with a modified legitimate invoice (simulate tampering)
        logger.info("\nTesting with a modified legitimate invoice (simulated tampering):")
        
        try:
            # Take a legitimate invoice and modify it slightly
            original_sample = test_split[0]
            original_image = original_sample['image']
            
            # Create a copy and modify it slightly
            modified_image = original_image.copy()
            draw = ImageDraw.Draw(modified_image)
            
            # Add a small modification (like changing an amount)
            draw.rectangle([50, 50, 200, 80], fill='white')
            draw.text((55, 55), "MODIFIED", fill='red', font=font)
            
            modified_result = detector.detect_fake_invoice(modified_image)
            
            status = "LEGITIMATE" if not modified_result['is_fake'] else "FAKE"
            logger.info(f"Modified Invoice Test: {status} (Confidence: {modified_result['confidence']:.2f})")
            logger.info(f"  Hash: {modified_result['hash'][:16] if modified_result['hash'] else 'None'}...")
            logger.info(f"  Reason: {modified_result['reason']}")
            logger.info(f"  Image size: {modified_image.size}")
            
        except Exception as e:
            logger.error(f"Error testing modified invoice: {e}")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_detector()
