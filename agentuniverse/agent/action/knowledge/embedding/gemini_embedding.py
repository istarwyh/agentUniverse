#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
from typing import List, Any

from google import genai
from langchain_core.embeddings import Embeddings as LCEmbeddings
from pydantic import Field
from typing_extensions import Optional

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.base.util.env_util import get_from_env


# @Time : 2025/2/13 12:10
# @Author : wozhapen
# @mail : wozhapen@gmail.com
# @FileName :gemini_embedding.py

class GeminiEmbedding(Embedding):
    """Gemini Embedding class that inherits from the base Embedding class."""

    client: Any = None
    gemini_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("GEMINI_EMBEDDING_API_KEY"))

    def get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Get embeddings for a list of texts using the Gemini API."""
        model_name = self.embedding_model_name or "text-embedding-004" #default model
        if self.client is None:
            self.client = genai.Client(api_key=self.gemini_api_key)
            # Gemini does not have a native proxy solution.
            # os.environ will proxy the whole application. It's only for test
            # os.environ['https_proxy'] = 'http://127.0.0.1:10808'
        embeddings = []

        for text in texts:
            try:
                response = self.client.models.embed_content(
                    model=model_name,
                    contents=text,
                )
                embeddings.append(response.embeddings[0].values)
            except Exception as e:
                print(f"Error generating embedding for text: {text}. Error: {e}")
                # Handle the error appropriately, e.g., return a zero vector or raise an exception
                embeddings.append([0.0] * (self.embedding_dims or 1536))  # Use a default dimension, or embedding_dims if specified.

        return embeddings

    async def async_get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Asynchronously get embeddings for a list of texts using the Gemini API."""
        #This implementation is synchronous because the Gemini API does not currently offer an official asynchronous client for embedding.
        #Consider implementing async batching or utilizing a ThreadPoolExecutor to wrap the synchronous call for better concurrency.
        return self.get_embeddings(texts, **kwargs)

    def as_langchain(self) -> LCEmbeddings:
        """Convert to a Langchain Embedding class."""
        #  This can be implemented to return an instance of a custom class extending from `langchain_core.embeddings.Embeddings`.
        #  However, since we are already using `google.generativeai` directly, this might be redundant.

        class GeminiLangchainEmbedding(LCEmbeddings):
            """Wrapper for Gemini Embeddings to conform to Langchain's Embeddings interface."""

            def embed_documents(self, texts: List[str]) -> List[List[float]]:
                """Embed a list of documents."""
                return self.get_embeddings(texts)

            def embed_query(self, text: str) -> List[float]:
                """Embed a single query."""
                return self.get_embeddings([text])[0]

        return GeminiLangchainEmbedding()