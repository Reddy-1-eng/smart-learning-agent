import ollama

class QueryAgent:
    def __init__(self, model_name="llama3:instruct"):
        # Use Ollama model instead of HuggingFace
        self.model_name = model_name

    def process(self, topic: str) -> str:
        """Clean and normalize topic using LLaMA (Ollama)."""
        # Prompt for topic refinement
        prompt = f"""
Refine and expand this learning topic to make it more specific and searchable: '{topic}'

Refined topic:
"""
        # Call Ollama
        response = ollama.chat(model=self.model_name, messages=[
            {"role": "user", "content": prompt}
        ])
        
        refined_text = response["message"]["content"].strip()

        # Extract the refined topic (everything after "Refined topic:")
        if "Refined topic:" in refined_text:
            refined_topic = refined_text.split("Refined topic:")[-1].strip()
            return refined_topic
        else:
            return refined_text if refined_text else topic.strip()
