"""
Simplified local version of Udyami AI backend - No authentication, no external APIs
"""
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import uuid
import logging
import glob
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel
from src.utils.document_extractor import DocumentExtractor


# ============================================================================
# Configuration
# ============================================================================

UPLOADS_BASE_DIR = Path("./uploads")
LOCAL_USER = "local_user"  # Single user for local mode

# ============================================================================
# Pydantic Models
# ============================================================================

class ProcessUrlRequest(BaseModel):
    urls: List[str]

class DownloadFileRequest(BaseModel):
    file_name: str
    file_type: str

class DeleteFileRequest(BaseModel):
    file_name: str

class SearchRequest(BaseModel):
    query: str
    user_id: str = LOCAL_USER

class SearchResponse(BaseModel):
    query: str
    result: str

# ============================================================================
# Local Storage Helper (replaces Firestore)
# ============================================================================

class LocalStorageHelper:
    def __init__(self):
        self.processes_dir = UPLOADS_BASE_DIR / "processes"
        self.processes_dir.mkdir(parents=True, exist_ok=True)
    
    def create_process_document(self, process_id: str, items: List[str], user_id: str):
        """Create a process tracking document"""
        process_data = {
            "process_id": process_id,
            "user_id": user_id,
            "items": items,
            "status": "processing",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "completed_at": None,
            "error": None
        }
        
        process_file = self.processes_dir / f"{process_id}.json"
        with open(process_file, "w") as f:
            json.dump(process_data, f, indent=2)
    
    def update_process_status(self, process_id: str, status: str, error: str = None):
        """Update process status"""
        process_file = self.processes_dir / f"{process_id}.json"
        if not process_file.exists():
            return
        
        with open(process_file, "r") as f:
            process_data = json.load(f)
        
        process_data["status"] = status
        process_data["updated_at"] = datetime.now().isoformat()
        if status == "completed":
            process_data["completed_at"] = datetime.now().isoformat()
        if error:
            process_data["error"] = error
        
        with open(process_file, "w") as f:
            json.dump(process_data, f, indent=2)
    
    def get_latest_processes(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Get latest processes for a user"""
        processes = []
        for process_file in self.processes_dir.glob("*.json"):
            try:
                with open(process_file, "r") as f:
                    data = json.load(f)
                    if data.get("user_id") == user_id:
                        processes.append(data)
            except:
                continue
        
        # Sort by created_at descending
        processes.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return processes[:limit]

# ============================================================================
# File Processing Helper
# ============================================================================

class LocalProcessHelper:
    def __init__(self, storage: LocalStorageHelper):
        self.storage = storage
    
    def get_user_dirs(self, user_id: str):
        """Get user directory structure"""
        base = UPLOADS_BASE_DIR / user_id
        return {
            "processing": base / "processing",
            "original": {
                "docs": base / "original" / "docs",
                "media": base / "original" / "media",
                "links": base / "original" / "links",
            },
            "processed": {
                "docs": base / "processed" / "docs",
                "media": base / "processed" / "media",
                "links": base / "processed" / "links",
            }
        }
    
    def ensure_dirs(self, user_id: str):
        """Create user directory structure"""
        dirs = self.get_user_dirs(user_id)
        dirs["processing"].mkdir(parents=True, exist_ok=True)
        for category_dir in dirs["original"].values():
            category_dir.mkdir(parents=True, exist_ok=True)
        for category_dir in dirs["processed"].values():
            category_dir.mkdir(parents=True, exist_ok=True)
    
    def determine_file_category(self, filename: str) -> str:
        """Determine file category based on extension"""
        ext = Path(filename).suffix.lower()
        media_exts = [".mp3", ".mp4", ".wav", ".m4a", ".avi", ".mov"]
        if ext in media_exts:
            return "media"
        return "docs"
    
    async def process_files_background(self, process_id: str, user_id: str, files: List[UploadFile]):
        """Process uploaded files in background"""
        try:
            self.ensure_dirs(user_id)
            dirs = self.get_user_dirs(user_id)
            
            for file in files:
                try:
                    # Determine category
                    category = self.determine_file_category(file.filename)
                    
                    # Generate unique filename
                    file_id = uuid.uuid4().hex[:8]
                    original_name = Path(file.filename).stem
                    extension = Path(file.filename).suffix
                    unique_name = f"{original_name}_{file_id}"
                    
                    # Save original file
                    original_path = dirs["original"][category] / f"{unique_name}{extension}"
                    with open(original_path, "wb") as f:
                        content = await file.read()
                        f.write(content)
                    
                    logger.info(f"Saved original file: {original_path}")
                    
                    # Extract text content from document
                    extracted_text = None
                    if category == "docs":
                        logger.info(f"Extracting text from: {original_path}")
                        extracted_text = DocumentExtractor.extract_text(original_path)
                        if extracted_text:
                            logger.info(f"Extracted {len(extracted_text)} characters from {file.filename}")
                        else:
                            logger.warning(f"No text extracted from {file.filename}")
                    
                    # Create summary
                    if extracted_text:
                        summary = DocumentExtractor.create_summary(extracted_text, max_length=300)
                    else:
                        summary = f"Local file: {file.filename}"
                    
                    # Create processed metadata
                    metadata = {
                        "old_name": file.filename,
                        "name": unique_name,
                        "summary": summary,
                        "tags": ["local", category],
                        "created_at": datetime.now().isoformat(),
                        "has_content": extracted_text is not None,
                        "content_length": len(extracted_text) if extracted_text else 0
                    }
                    
                    meta_path = dirs["processed"][category] / f"{unique_name}.meta"
                    with open(meta_path, "w", encoding="utf-8") as f:
                        json.dump(metadata, f, indent=2, ensure_ascii=False)
                    
                    # Create markdown with full extracted content
                    if extracted_text:
                        md_content = f"""# {file.filename}

**File:** {unique_name}{extension}
**Category:** {category}
**Uploaded:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Content Length:** {len(extracted_text)} characters

---

## Extracted Content

{extracted_text}
"""
                    else:
                        md_content = f"""# {file.filename}

**File:** {unique_name}{extension}
**Category:** {category}
**Uploaded:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

File uploaded locally. Text extraction not available for this file type.
"""
                    
                    md_path = dirs["processed"][category] / f"{unique_name}.md"
                    with open(md_path, "w", encoding="utf-8") as f:
                        f.write(md_content)
                    
                    logger.info(f"Processed file: {file.filename} -> {unique_name}")
                
                except Exception as e:
                    logger.error(f"Error processing file {file.filename}: {e}", exc_info=True)
                    continue
            
            self.storage.update_process_status(process_id, "completed")
            logger.info(f"Process {process_id} completed successfully")
        
        except Exception as e:
            logger.error(f"Error in process {process_id}: {e}", exc_info=True)
            self.storage.update_process_status(process_id, "failed", str(e))
    
    async def process_links_background(self, process_id: str, user_id: str, urls: List[str]):
        """Process URLs in background"""
        try:
            self.ensure_dirs(user_id)
            dirs = self.get_user_dirs(user_id)
            
            for url in urls:
                try:
                    # Generate unique name for link
                    link_id = uuid.uuid4().hex[:8]
                    link_name = f"link_{link_id}"
                    
                    # Create metadata
                    metadata = {
                        "old_name": url,
                        "name": link_name,
                        "summary": f"Link: {url}",
                        "tags": ["link", "url"],
                        "created_at": datetime.now().isoformat()
                    }
                    
                    meta_path = dirs["processed"]["links"] / f"{link_name}.meta"
                    with open(meta_path, "w") as f:
                        json.dump(metadata, f, indent=2)
                    
                    # Create simple markdown content
                    md_content = f"# Link\n\nURL: {url}\n\nProcessed locally without external fetching.\n"
                    md_path = dirs["processed"]["links"] / f"{link_name}.md"
                    with open(md_path, "w") as f:
                        f.write(md_content)
                    
                    logger.info(f"Processed link: {url} -> {link_name}")
                
                except Exception as e:
                    logger.error(f"Error processing URL {url}: {e}")
                    continue
            
            self.storage.update_process_status(process_id, "completed")
            logger.info(f"Process {process_id} completed successfully")
        
        except Exception as e:
            logger.error(f"Error in process {process_id}: {e}")
            self.storage.update_process_status(process_id, "failed", str(e))

# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(title="Udyami AI Local Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize helpers
storage = LocalStorageHelper()
process_helper = LocalProcessHelper(storage)

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
def health():
    return {"health": "ok", "mode": "local"}

@app.post("/upload")
async def upload(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
):
    """Upload files for processing"""
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed")
    
    process_id = uuid.uuid4().hex
    logger.info(f"Upload received: {len(files)} files, process_id: {process_id}")
    
    storage.create_process_document(
        process_id,
        [file.filename for file in files],
        LOCAL_USER
    )
    
    background_tasks.add_task(
        process_helper.process_files_background,
        process_id,
        LOCAL_USER,
        files
    )
    
    return {"message": "Files uploaded successfully", "process_id": process_id}

@app.post("/process-urls")
async def process_urls(
    background_tasks: BackgroundTasks,
    request: ProcessUrlRequest,
):
    """Process URLs"""
    process_id = uuid.uuid4().hex
    logger.info(f"URL processing: {len(request.urls)} URLs, process_id: {process_id}")
    
    storage.create_process_document(
        process_id,
        request.urls,
        LOCAL_USER
    )
    
    background_tasks.add_task(
        process_helper.process_links_background,
        process_id,
        LOCAL_USER,
        request.urls
    )
    
    return {"message": "URLs submitted for processing", "process_id": process_id}

@app.get("/processes/recent")
def get_recent_processes():
    """Get recent processes"""
    processes = storage.get_latest_processes(LOCAL_USER, limit=5)
    return {"processes": processes}

@app.get("/files/processed")
def get_processed_files():
    """Get all processed files"""
    base_dir = UPLOADS_BASE_DIR / LOCAL_USER / "processed"
    
    categories = {
        "docs": [],
        "links": [],
        "media": [],
    }
    
    for category in categories.keys():
        category_dir = base_dir / category
        if not category_dir.is_dir():
            continue
        
        for entry in category_dir.iterdir():
            if entry.name.endswith(".meta"):
                try:
                    with open(entry, "r") as f:
                        data = json.load(f)
                        categories[category].append(data)
                except:
                    continue
    
    return categories

@app.post("/download")
async def download_file(request: DownloadFileRequest):
    """Download original file"""
    if request.file_type not in ["docs", "media"]:
        raise HTTPException(
            status_code=400,
            detail="file_type must be either 'docs' or 'media'"
        )
    
    original_dir = UPLOADS_BASE_DIR / LOCAL_USER / "original" / request.file_type
    
    if not original_dir.is_dir():
        raise HTTPException(status_code=404, detail="Directory not found")
    
    # Find file with matching name
    pattern = str(original_dir / f"{request.file_name}.*")
    matching_files = glob.glob(pattern)
    
    if not matching_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = matching_files[0]
    original_filename = Path(file_path).name
    
    return FileResponse(
        path=file_path,
        filename=original_filename,
        media_type="application/octet-stream",
    )

@app.delete("/files")
async def delete_file(request: DeleteFileRequest):
    """Delete a file"""
    base_dir = UPLOADS_BASE_DIR / LOCAL_USER
    processed_dir = base_dir / "processed"
    original_dir = base_dir / "original"
    
    deleted_files = []
    found_any = False
    
    categories = ["docs", "media", "links"]
    
    # Delete from processed
    for category in categories:
        category_dir = processed_dir / category
        if category_dir.exists():
            meta_file = category_dir / f"{request.file_name}.meta"
            if meta_file.exists():
                meta_file.unlink()
                deleted_files.append(str(meta_file))
                found_any = True
            
            md_file = category_dir / f"{request.file_name}.md"
            if md_file.exists():
                md_file.unlink()
                deleted_files.append(str(md_file))
                found_any = True
    
    # Delete from original
    for category in categories:
        category_dir = original_dir / category
        if category_dir.exists():
            for file_path in category_dir.glob(f"{request.file_name}.*"):
                file_path.unlink()
                deleted_files.append(str(file_path))
                found_any = True
    
    if not found_any:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {
        "message": f"Successfully deleted file '{request.file_name}'",
        "deleted_files": deleted_files,
        "count": len(deleted_files)
    }

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """Enhanced local search with content ranking"""
    base_dir = UPLOADS_BASE_DIR / LOCAL_USER / "processed"
    
    # Extract keywords from query (split and clean)
    query_lower = request.query.lower()
    
    # Extract meaningful keywords (remove common words)
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                  'of', 'with', 'by', 'from', 'about', 'as', 'is', 'was', 'are', 'were',
                  'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
                  'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can',
                  'your', 'my', 'their', 'our', 'his', 'her', 'its', 'this', 'that',
                  'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}
    
    # Extract keywords
    words = query_lower.replace(',', ' ').replace('.', ' ').split()
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    
    # If no keywords extracted, use original query
    if not keywords:
        keywords = [query_lower]
    
    logger.info(f"Search query: '{request.query}' -> Keywords: {keywords}")
    
    results = []
    
    # Search through all markdown files
    for category in ["docs", "media", "links"]:
        category_dir = base_dir / category
        if not category_dir.exists():
            continue
        
        for md_file in category_dir.glob("*.md"):
            try:
                # Read the markdown content
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                content_lower = content.lower()
                
                # Check if any keyword matches
                matches = [kw for kw in keywords if kw in content_lower]
                
                if matches:
                    # Load metadata for better context
                    meta_file = md_file.with_suffix('.meta')
                    file_info = {"name": md_file.stem, "category": category}
                    
                    if meta_file.exists():
                        try:
                            with open(meta_file, "r", encoding="utf-8") as mf:
                                metadata = json.load(mf)
                                file_info["original_name"] = metadata.get("old_name", md_file.stem)
                                file_info["summary"] = metadata.get("summary", "")
                        except:
                            pass
                    
                    # Find relevant excerpts for each matching keyword
                    lines = content.split('\n')
                    relevant_lines = []
                    
                    for keyword in matches[:3]:  # Limit to top 3 keywords
                        for i, line in enumerate(lines):
                            if keyword in line.lower():
                                # Get context around the match
                                start = max(0, i - 2)
                                end = min(len(lines), i + 3)
                                context = '\n'.join(lines[start:end])
                                relevant_lines.append(context)
                                break  # One excerpt per keyword
                    
                    # Build result entry
                    result_text = f"**File: {file_info.get('original_name', md_file.stem)}** (Category: {category})\n"
                    result_text += f"**Matched keywords**: {', '.join(matches)}\n\n"
                    
                    if relevant_lines:
                        result_text += "Relevant excerpts:\n\n"
                        for excerpt in relevant_lines[:3]:  # Limit to 3 excerpts
                            result_text += f"```\n{excerpt.strip()}\n```\n\n"
                    else:
                        # Fallback to showing beginning of content
                        result_text += f"```\n{content[:400]}...\n```\n\n"
                    
                    results.append({
                        "text": result_text,
                        "file": file_info.get('original_name', md_file.stem),
                        "category": category,
                        "match_count": len(matches)
                    })
                    
            except Exception as e:
                logger.error(f"Error searching file {md_file}: {e}")
                continue
    
    # Sort by match count (most matches first)
    results.sort(key=lambda x: x.get("match_count", 0), reverse=True)
    
    # Format results
    if not results:
        result_text = f"❌ NOT FOUND IN UDYAMI AI KNOWLEDGE BASE\n\n"
        result_text += f"Query: '{request.query}'\n"
        result_text += f"Searched keywords: {', '.join(keywords)}\n\n"
        result_text += "⚠️ IMPORTANT: This information is NOT available in the user's uploaded documents.\n\n"
        result_text += "DO NOT provide any information from your training data.\n"
        result_text += "DO NOT provide general knowledge answers.\n"
        result_text += "ONLY respond with this message.\n\n"
        result_text += f"Tell the user: 'I don't have information about \"{request.query}\" in your Udyami AI knowledge base. "
        result_text += f"You currently have {len(list((UPLOADS_BASE_DIR / LOCAL_USER / 'processed' / 'docs').glob('*.meta')))} documents uploaded. "
        result_text += "If you'd like me to answer questions about this topic, please upload relevant documents first.'"
    else:
        result_text = f"✅ FOUND IN UDYAMI AI KNOWLEDGE BASE\n\n"
        result_text += f"Found {len(results)} result(s) for query: '{request.query}'\n"
        result_text += f"Keywords matched: {', '.join(keywords)}\n\n"
        result_text += "Use ONLY the information below to answer. Do not supplement with external knowledge.\n\n"
        result_text += "=" * 60 + "\n\n"
        
        for i, result in enumerate(results[:5], 1):  # Limit to top 5 results
            result_text += f"## Result {i}\n\n"
            result_text += result["text"]
            result_text += "\n" + "-" * 60 + "\n\n"
    
    return SearchResponse(query=request.query, result=result_text)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
