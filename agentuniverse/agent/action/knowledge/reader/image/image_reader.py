# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/2/11 21:21
# @Author  : wozhapen
# @Email   : wozhapen@gmail.com
# @FileName: image_reader.py

from pathlib import Path
from typing import List, Optional, Dict, Union

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


class ImageReader(Reader):
    """Image reader using easyocr."""
    language: list[str] = ['en']
    gpu: bool = False
    reader: Reader = None

    def __init__(self, language=None, gpu: bool = False):
        """
        Initializes the EasyOCRReader.

        Args:
            language: The language to use for OCR (e.g., "en" for English, "ch_sim" for chinese).
            gpu: Whether to use GPU for OCR (requires CUDA).  Set to False if no GPU.
        """
        super().__init__()  # Call the Reader's __init__ method
        if language is not None:
            self.language = language
        self.gpu = gpu

    def _load_data(self, file: Union[str, Path], ext_info: Optional[Dict] = None) -> List[Document]:
        """Parse the image file and extract text using easyocr."""
        try:
            import easyocr
        except ImportError as e:
            raise ImportError(
                "easyocr is required. Install with: pip install easyocr"
            ) from e

        if isinstance(file, str):
            file = Path(file)

        try:
            # Initialize the reader only once
            reader = easyocr.Reader(lang_list=self.language, gpu=self.gpu)

            results = reader.readtext(str(file))  # easyocr expects a string path

            text = "\n".join([result[1] for result in results])  # Join the extracted text

            metadata = {"file_name": file.name}
            if ext_info is not None:
                metadata.update(ext_info)

            return [Document(text=text, metadata=metadata)]
        except Exception as e:
            print(f"Error processing image {file}: {e}")
            return []
