"""
Script to reprocess existing documents with text extraction
"""
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.document_extractor import DocumentExtractor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

UPLOADS_BASE_DIR = Path("./uploads")
LOCAL_USER = "local_user"


def reprocess_documents():
    """Reprocess all existing documents to extract text content"""
    
    base_dir = UPLOADS_BASE_DIR / LOCAL_USER
    original_dir = base_dir / "original"
    processed_dir = base_dir / "processed"
    
    if not original_dir.exists():
        logger.error(f"Original directory not found: {original_dir}")
        return
    
    processed_count = 0
    error_count = 0
    
    # Process documents
    for category in ["docs", "media", "links"]:
        category_original = original_dir / category
        category_processed = processed_dir / category
        
        if not category_original.exists():
            logger.info(f"Skipping category {category} - directory not found")
            continue
        
        category_processed.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"\nProcessing category: {category}")
        logger.info("=" * 60)
        
        for file_path in category_original.iterdir():
            if file_path.is_file():
                try:
                    logger.info(f"\nProcessing: {file_path.name}")
                    
                    # Extract text content
                    extracted_text = None
                    if category == "docs":
                        extracted_text = DocumentExtractor.extract_text(file_path)
                        if extracted_text:
                            logger.info(f"  ✓ Extracted {len(extracted_text)} characters")
                        else:
                            logger.warning(f"  ⚠ No text extracted")
                    
                    # Get file info
                    file_stem = file_path.stem
                    file_ext = file_path.suffix
                    
                    # Create summary
                    if extracted_text:
                        summary = DocumentExtractor.create_summary(extracted_text, max_length=300)
                    else:
                        summary = f"Local file: {file_path.name}"
                    
                    # Update metadata
                    metadata = {
                        "old_name": file_path.name,
                        "name": file_stem,
                        "summary": summary,
                        "tags": ["local", category, "reprocessed"],
                        "created_at": datetime.now().isoformat(),
                        "has_content": extracted_text is not None,
                        "content_length": len(extracted_text) if extracted_text else 0
                    }
                    
                    meta_path = category_processed / f"{file_stem}.meta"
                    with open(meta_path, "w", encoding="utf-8") as f:
                        json.dump(metadata, f, indent=2, ensure_ascii=False)
                    logger.info(f"  ✓ Updated metadata: {meta_path.name}")
                    
                    # Create/update markdown with full content
                    if extracted_text:
                        md_content = f"""# {file_path.name}

**File:** {file_stem}{file_ext}
**Category:** {category}
**Reprocessed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Content Length:** {len(extracted_text)} characters

---

## Extracted Content

{extracted_text}
"""
                    else:
                        md_content = f"""# {file_path.name}

**File:** {file_stem}{file_ext}
**Category:** {category}
**Reprocessed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

File uploaded locally. Text extraction not available for this file type.
"""
                    
                    md_path = category_processed / f"{file_stem}.md"
                    with open(md_path, "w", encoding="utf-8") as f:
                        f.write(md_content)
                    logger.info(f"  ✓ Created markdown: {md_path.name}")
                    
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"  ✗ Error processing {file_path.name}: {e}")
                    error_count += 1
                    continue
    
    logger.info("\n" + "=" * 60)
    logger.info(f"Reprocessing complete!")
    logger.info(f"  Successfully processed: {processed_count} files")
    logger.info(f"  Errors: {error_count} files")
    logger.info("=" * 60)


if __name__ == "__main__":
    logger.info("Starting document reprocessing...")
    logger.info(f"Base directory: {UPLOADS_BASE_DIR.absolute()}")
    reprocess_documents()
