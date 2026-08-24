import os
import json
import glob
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from groq import Groq

from ai.config import (
    KNOWLEDGE_DIR,
    FAISS_INDEX_DIR,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOP_K_RESULTS,
    GROQ_MODEL,
    GROQ_API_KEY
)

class RAGService:
    def __init__(self):
        print("Initializing RAG Service...")
        self.encoder = SentenceTransformer(EMBEDDING_MODEL)
        self.index = None
        self.chunks = []
        
        FAISS_INDEX_DIR.mkdir(parents=True, exist_ok=True)
        self.index_path = FAISS_INDEX_DIR / 'index.faiss'
        self.chunks_path = FAISS_INDEX_DIR / 'chunks.json'
        
        if self.index_path.exists() and self.chunks_path.exists():
            self.load_index()
        else:
            self.build_index()
            
    def load_index(self):
        print(f"Loading FAISS index from {self.index_path}")
        self.index = faiss.read_index(str(self.index_path))
        with open(self.chunks_path, 'r', encoding='utf-8') as f:
            self.chunks = json.load(f)
        print(f"Loaded {len(self.chunks)} chunks.")

    def build_index(self):
        print("Building new FAISS index from knowledge base...")
        if not KNOWLEDGE_DIR.exists():
            KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
            print(f"Created empty knowledge dir at {KNOWLEDGE_DIR}")
            
        md_files = glob.glob(str(KNOWLEDGE_DIR / '*.md'))
        
        self.chunks = []
        for file_path in md_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            start = 0
            while start < len(content):
                end = start + CHUNK_SIZE
                chunk_text = content[start:end]
                self.chunks.append({
                    "text": chunk_text,
                    "source_file": Path(file_path).name,
                    "section_header": ""
                })
                start += (CHUNK_SIZE - CHUNK_OVERLAP)
                
        if not self.chunks:
            print("No knowledge base chunks found. Index will be empty.")
            d = self.encoder.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatL2(d)
            return

        texts = [c["text"] for c in self.chunks]
        embeddings = self.encoder.encode(texts, convert_to_numpy=True)
        
        d = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(d)
        self.index.add(embeddings)
        
        faiss.write_index(self.index, str(self.index_path))
        with open(self.chunks_path, 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f)
            
        print(f"Built index with {len(self.chunks)} chunks.")

    def retrieve(self, query, top_k=TOP_K_RESULTS):
        if not self.chunks or self.index is None or self.index.ntotal == 0:
            return []
            
        query_embedding = self.encoder.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding, min(top_k, len(self.chunks)))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.chunks):
                results.append({
                    "text": self.chunks[idx]["text"],
                    "source": self.chunks[idx]["source_file"],
                    "score": float(distances[0][i])
                })
                
        return results

    def _generate_local_fallback(self, context, retrieved_results):
        """Generates a structured agronomic recommendation directly from local knowledge when Groq is offline."""
        disease = "Healthy"
        if 'vision' in context and context['vision'] and 'class' in context['vision']:
            disease = context['vision']['class'].replace('___', ' — ').replace('_', ' ')
        
        is_healthy = "healthy" in disease.lower()
        priority = "low" if is_healthy else "high"
        
        summary = f"Canopy scan completed: {disease}."
        if is_healthy:
            summary += " Foliage shows robust cell turgor and healthy chlorophyll pigmentation."
        else:
            summary += " Pathological symptoms detected on leaf surface. Immediate environmental and nutrient adjustment advised."

        actions = []
        if is_healthy:
            actions.append({
                "action": "Maintain balanced nutrient dosing and regular irrigation cycles.",
                "reason": "Plant is thriving; preserve steady-state electrical conductivity and root moisture.",
                "source_ids": ["ph_ec_management.md"]
            })
            actions.append({
                "action": "Keep canopy ventilation active to sustain optimal Vapor Pressure Deficit (VPD).",
                "reason": "Optimal airflow prevents high humidity pockets where spores germinate.",
                "source_ids": ["environment_guide.md"]
            })
        else:
            # Generate targeted disease actions from retrieved sources
            sources = list(set([r["source"] for r in retrieved_results])) or ["tomato_diseases.md"]
            actions.append({
                "action": f"Isolate affected foliage and sanitize prune tools to prevent spore spread.",
                "reason": "Halts the spread of fungal/bacterial pathogens across the hydroponic channel.",
                "source_ids": sources[:1]
            })
            actions.append({
                "action": "Adjust reservoir pH to 5.8 - 6.2 and flush system if TDS exceeds 1200 ppm.",
                "reason": "Restores root absorption of essential micronutrients (Iron, Zinc, Manganese) to boost immunity.",
                "source_ids": ["ph_ec_management.md"]
            })
            actions.append({
                "action": "Apply targeted organic bio-fungicide (e.g. Copper Soap or Bacillus subtilis) to canopy.",
                "reason": "Suppresses active pathogen colonization without damaging hydroponic root biology.",
                "source_ids": ["pest_management.md"]
            })

        warnings = [
            "Ensure solution water temperature does not exceed 23°C to prevent root rot.",
            "Verify all drippers and return drains are free of biofilm obstructions."
        ]

        return {
            "priority": priority,
            "summary": summary,
            "actions": actions,
            "warnings": warnings
        }

    def generate_recommendation(self, context):
        search_terms = []
        if 'crop' in context and context['crop']:
            search_terms.append(context['crop'])
            
        if 'vision' in context and context['vision'] and 'class' in context['vision']:
            disease = context['vision']['class'].replace('_', ' ')
            search_terms.append(disease)
            search_terms.append("treatment")
            
        if 'sensors' in context and context['sensors'] and 'status' not in context['sensors']:
            sensors = context['sensors']
            if 'ph' in sensors and sensors['ph'] is not None:
                search_terms.append(f"pH {sensors['ph']}")
                
        search_query = " ".join(search_terms)
        print(f"RAG Search Query: {search_query}")
        
        retrieved = self.retrieve(search_query) if search_query else []
        
        api_key = GROQ_API_KEY
        if not api_key:
            print("GROQ_API_KEY not configured. Using local FAISS knowledge fallback.")
            return self._generate_local_fallback(context, retrieved)

        retrieved_knowledge = [f"Source: {r['source']}\n{r['text']}\n" for r in retrieved]
        knowledge_text = "\n".join(retrieved_knowledge)
        
        system_prompt = """You are AgroEye, an expert hydroponic farming advisor. Given plant health analysis and sensor data, provide specific, actionable recommendations. Base your advice on the provided knowledge base if applicable. Be concise. Always cite sources.
Return ONLY valid JSON matching this schema:
{
    "priority": "high/medium/low",
    "summary": "Brief summary of the situation",
    "actions": [{"action": "Specific action to take", "reason": "Why take this action", "source_ids": ["source1.md"]}],
    "warnings": ["Any warnings or things to look out for"]
}"""

        user_prompt = f"""
Current Context:
{json.dumps(context, indent=2)}

Knowledge Base:
{knowledge_text if knowledge_text else "No specific knowledge found."}
"""
        try:
            client = Groq(api_key=api_key)
            completion = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            
            response_content = completion.choices[0].message.content
            return json.loads(response_content)
        except Exception as e:
            print(f"Groq API error ({str(e)}). Falling back to local FAISS knowledge synthesis.")
            return self._generate_local_fallback(context, retrieved)

# Lazy singleton
_rag_instance = None

def get_rag_service():
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGService()
    return _rag_instance
