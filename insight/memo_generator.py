import os
import requests
import json
from typing import Dict, List

class OllamaClient:
    """Simple client for local Ollama instance."""
    def __init__(self, base_url: str = None, model: str = "llama3"):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        
        # Combine system and user prompt for simple completion models, or use chat endpoint if available
        # Using generate endpoint typically works well for general instruction
        full_prompt = f"System: {system_prompt}\n\nUser: {user_prompt}\n\nAssistant:"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            print(f"Ollama Connection Error: {e}")
            return None

class MemoGenerator:
    """Generates the Dalio-style insight memo."""
    
    def __init__(self):
        # We assume Ollama is running
        self.client = OllamaClient()

    def generate_memo(self, context: Dict, principles: List[Dict]) -> str:
        """
        Synthesizes the regime and principles into a memo.
        """
        # Construct the Prompt
        # 1. System Role
        system_prompt = """You are Ray Dalio's AI Associate. 
        Your goal is to write a clear, principle-based investment memo.
        
        Style Guide:
        - Radical Truth: Don't sugarcoat.
        - Mechanism: Explain the 'machine' (cause-effect).
        - Historical: Cite history.
        - Humble: Admit what you don't know.
        """
        
        # 2. Context Construction
        date = context.get('date', 'Unknown Date')
        regime = context.get('regime', 'Unknown')
        details = context.get('details', {})
        
        context_str = f"Date: {date}\nCurrent Regime: {regime}\n"
        context_str += f"metrics: {details}\n"
        
        # 3. Principles
        principles_str = "\n".join([f"- {p['content']} (Source: {p['source']})" for p in principles])
        
        user_prompt = f"""
        CONTEXT:
        {context_str}
        
        RELEVANT PRINCIPLES:
        {principles_str}
        
        TASK:
        Write a short daily insight memo (max 300 words).
        1. Diagnose the mechanism: Why are we in this regime?
        2. Apply the principles: What usually happens next?
        3. Recommend a general portfolio bias (Risk On/Off, Gold/Bonds/Stocks).
        """
        
        response_text = self.client.generate(system_prompt, user_prompt)
        
        if response_text:
            return response_text
            
        print("WARNING: Ollama unavailable. Returning MOCK memo.")
        return """BASIC INSIGHT (MOCK - OLLAMA DOWN):
             
             The current regime is characterized by slowing growth and rising inflation (Stagflation). 
             
             PRINCIPLES:
             History shows that in these periods, cash is trash and real assets (Gold, Commodities) outperform. The central bank is stuck between a rock (inflation) and a hard place (recession).
             
             ACTION:
             Reduce duration. Buy Gold.
             """

if __name__ == "__main__":
    # Mock
    mg = MemoGenerator()
    ctx = {
        "date": "1973-11-01", 
        "regime": "Stagflation (Growth-, Inflation+)",
        "details": {"inflation_yoy": 0.08, "growth_yoy": -0.01}
    }
    princs = [{"content": "When inflation is high and growth is low, hold real assets.", "source": "Principles.pdf"}]
    print(mg.generate_memo(ctx, princs))
