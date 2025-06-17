from datasets import load_dataset
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_dataset_structure():
    """Debug the dataset structure to understand the format"""
    try:
        logger.info("Loading dataset for debugging...")
        dataset = load_dataset("naver-clova-ix/cord-v2")
        
        logger.info("=== Dataset Structure Debug ===")
        logger.info(f"Dataset type: {type(dataset)}")
        logger.info(f"Dataset keys: {list(dataset.keys())}")
        
        for split_name in dataset.keys():
            split_data = dataset[split_name]
            logger.info(f"\n=== {split_name.upper()} Split ===")
            logger.info(f"Split type: {type(split_data)}")
            logger.info(f"Split length: {len(split_data)}")
            
            if hasattr(split_data, 'features'):
                logger.info(f"Features: {split_data.features}")
            
            # Get first sample
            if len(split_data) > 0:
                sample = split_data[0]
                logger.info(f"Sample type: {type(sample)}")
                
                if isinstance(sample, dict):
                    logger.info(f"Sample keys: {list(sample.keys())}")
                    for key, value in sample.items():
                        logger.info(f"  {key}: {type(value)}")
                        if key == 'image' and hasattr(value, 'size'):
                            logger.info(f"    Image size: {value.size}")
                        elif key == 'ground_truth':
                            logger.info(f"    Ground truth type: {type(value)}")
                            if isinstance(value, (dict, str)):
                                logger.info(f"    Ground truth preview: {str(value)[:100]}...")
                else:
                    logger.info(f"Sample attributes: {dir(sample)}")
                
                # Try to access image directly
                try:
                    if isinstance(sample, dict) and 'image' in sample:
                        image = sample['image']
                        logger.info(f"Image accessed successfully: {type(image)}")
                        if hasattr(image, 'size'):
                            logger.info(f"Image size: {image.size}")
                    else:
                        logger.warning("Could not access image from sample")
                except Exception as e:
                    logger.error(f"Error accessing image: {e}")
        
        # Test batch access
        logger.info("\n=== Batch Access Test ===")
        try:
            test_batch = dataset['test'][:3]
            logger.info(f"Batch type: {type(test_batch)}")
            if isinstance(test_batch, dict):
                logger.info(f"Batch keys: {list(test_batch.keys())}")
                for key, value in test_batch.items():
                    logger.info(f"  {key}: {type(value)} (length: {len(value) if hasattr(value, '__len__') else 'N/A'})")
        except Exception as e:
            logger.error(f"Error with batch access: {e}")
            
    except Exception as e:
        logger.error(f"Error loading dataset: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    debug_dataset_structure()
