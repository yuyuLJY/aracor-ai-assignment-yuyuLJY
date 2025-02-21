# aracor-ai-assignment-yuyuLJY# aracor-ai-assignment-yuyuLJY

# Installation

# API Response Schemas

### Document Processor Responses

Success Response


```json
{
  "success": true,
  "code": 200,
  "message": "Text extracted successfully",
  "data": {
    "file_path": "path/to/file/P18.pdf",
    "file_type": "pdf",
    "content": "Extracted text..."
  }
}
```

Failure Response
```json
{
  "success": false,
  "code": 400,
  "message": "Unsupported file format. Only PDF, TXT, and DOCX are allowed.",
  "data": null
}
```

```json
{
  "success": false,
  "code": 400,
  "message": "File not found",
  "data": null
}
```

```json
{
  "success": false,
  "code": 500,
  "message": "Error processing document",
  "data": null
}
```

### Summary Generator Responses

Success Response
```json
{
  "success": true,
  "code": 200,
  "message": "Summary generated successfully",
  "data": {
    "status": "success",
    "summary": "Generated summary text..."
  }
}
```
```json
{
  "success": true,
  "code": 206,
  "message": "Timeout occurred: [error details]. Returning partial results.",
  "data": {
    "status": "partial",
    "summary": "Partial summary result..."
  }
}
```

Failure Response
```json
{
  "success": false,
  "code": 500,
  "message": "Error generating summary",
  "data": null
}
```

# Run all functions
```python
#!/usr/bin/env python3
import sys
sys.path.append("src/")

from src.processors.document import DocumentProcessor
from src.services.model_manager import ModelManager
from src.services.summary import SummaryGenerator

file_path = "tests/test_files/P18.pdf"
processor = DocumentProcessor(file_path)
text_content = processor.extract_text()

if text_content.data is not None:
    text = text_content.data.content
    model_manager = ModelManager().get_model('openai')
    summarizer = SummaryGenerator(model_manager)
    summary = summarizer.generate_summary(text, summary_type="bullet points")
    print("Generated Summary:", summary)
```

# Configuration
The project uses environment variables for configuration. Update the .env file with your API keys and model provider settings.

# Run pytest
(haven't tested Anthropic as token expired)

To run the tests, use the following command:
```sh
pytest tests/test_summary_generator.py -v
```

# Run pylint test
```sh
pylint --fail-under=9.0 src/
```

# Logging
Logs are stored in the /logs directory. 

# TODO
- Test summarization quality
- Refine timeout processing
- create PromptManager, chunkSizeManager