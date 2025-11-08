import openai
import os
from typing import List, Dict
import numpy as np

class SemanticCodeSearch:
    """Semantic search for similar code patterns"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        openai.api_key = self.api_key
        self.code_embeddings = {}
    
    def generate_embedding(self, code: str) -> List[float]:
        """Generate embedding vector for code"""
        response = openai.Embedding.create(
            model='text-embedding-ada-002',
            input=code
        )
        return response['data'][0]['embedding']
    
    def index_codebase(self, files: Dict[str, str]):
        """Index entire codebase for semantic search"""
        for file_path, code in files.items():
            embedding = self.generate_embedding(code)
            self.code_embeddings[file_path] = {
                'code': code,
                'embedding': embedding
            }
    
    def find_similar_code(self, query_code: str, top_k: int = 5) -> List[Dict]:
        """Find similar code snippets"""
        query_embedding = self.generate_embedding(query_code)
        
        similarities = []
        for file_path, data in self.code_embeddings.items():
            similarity = self._cosine_similarity(
                query_embedding, 
                data['embedding']
            )
            similarities.append({
                'file': file_path,
                'similarity': similarity,
                'code': data['code']
            })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]
    
    def detect_duplicate_logic(self, threshold: float = 0.85) -> List[Dict]:
        """Detect duplicate or similar logic across codebase"""
        duplicates = []
        
        files = list(self.code_embeddings.keys())
        for i, file1 in enumerate(files):
            for file2 in files[i+1:]:
                similarity = self._cosine_similarity(
                    self.code_embeddings[file1]['embedding'],
                    self.code_embeddings[file2]['embedding']
                )
                
                if similarity > threshold:
                    duplicates.append({
                        'file1': file1,
                        'file2': file2,
                        'similarity': similarity,
                        'recommendation': 'Consider extracting to shared module'
                    })
        
        return duplicates
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
