#!/usr/bin/env python3
import sys

sys.path.append("src/")

# from src.config.settings import ConfigSettings
# settings = ConfigSettings()
# print(settings.model_dump())

from src.processors.document import DocumentProcessor
from src.services.model_manager import ModelManager
from src.services.summary import SummaryGenerator

file_path = "tests/test_files/P18.pdf"
processor = DocumentProcessor(file_path)
text_content = processor.extract_text()
# print(text_content)

if text_content.data is not None:
    text = text_content.data.content
    model = ModelManager().get_model('openai') # factory pattern
    summarizer = SummaryGenerator(model) # dependency injection
    summary = summarizer.generate_summary(text, summary_type="bullet points")
    print("Generated Summary:", summary)