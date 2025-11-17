import httpx
import logging
from ..orchestrator.config import settings

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.mistral_key = settings.MISTRAL_API_KEY
        self.openrouter_key = settings.OPENROUTER_API_KEY

    async def generate(self, messages, provider='auto', model=None, temperature=0.7):
        if provider == 'auto':
            # Default strategy: use Mistral for extraction/logic, Gemini (via OpenRouter) for creative/pedagogy
            # For now, let's default to Mistral if not specified, or Gemini if explicitly requested
            provider = 'mistral'

        if provider == 'mistral':
            return await self._call_mistral(messages, model or 'mistral-large-latest', temperature)
        elif provider == 'openrouter':
            return await self._call_openrouter(messages, model or 'google/gemma-3-27b-it:free', temperature)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def _call_mistral(self, messages, model, temperature):
        url = 'https://api.mistral.ai/v1/chat/completions'
        headers = {'Authorization': f'Bearer {self.mistral_key}'}
        body = {
            'model': model,
            'messages': messages,
            'temperature': temperature
        }
        async with httpx.AsyncClient() as client:
            try:
                r = await client.post(url, json=body, headers=headers, timeout=60)
                r.raise_for_status()
                return r.json()['choices'][0]['message']['content']
            except Exception as e:
                logger.error(f"Mistral call failed: {e}")
                raise

    async def _call_openrouter(self, messages, model, temperature):
        url = 'https://openrouter.ai/api/v1/chat/completions'
        headers = {
            'Authorization': f'Bearer {self.openrouter_key}',
            'HTTP-Referer': 'https://flowmind.local', # Required by OpenRouter
            'X-Title': 'FlowMind'
        }
        # OpenRouter/Gemini expects standard OpenAI format
        body = {
            'model': model,
            'messages': messages,
            'temperature': temperature
        }
        async with httpx.AsyncClient() as client:
            try:
                r = await client.post(url, json=body, headers=headers, timeout=60)
                r.raise_for_status()
                return r.json()['choices'][0]['message']['content']
            except Exception as e:
                logger.error(f"OpenRouter call failed: {e}")
                raise


    async def embed(self, text):
        """Generate embeddings using Mistral's embedding model"""
        url = 'https://api.mistral.ai/v1/embeddings'
        headers = {'Authorization': f'Bearer {self.mistral_key}'}
        body = {
            'model': 'mistral-embed',
            'input': [text]  # API expects a list
        }
        async with httpx.AsyncClient() as client:
            try:
                r = await client.post(url, json=body, headers=headers, timeout=60)
                r.raise_for_status()
                # Returns list of embeddings, we take the first one
                return r.json()['data'][0]['embedding']
            except Exception as e:
                logger.error(f"Mistral embed call failed: {e}")
                raise


    async def process_vision(self, image_path, prompt):
        """
        Process image with vision model using fallback chain:
        1. Try google/gemma-3-27b-it:free (OpenRouter)
        2. Fall back to mistralai/mistral-small-3.1-24b-instruct:free (OpenRouter)
        3. Final fallback: pixtral-12b-2409 (Mistral API)
        
        Args:
            image_path: Path to image file
            prompt: Text prompt for the vision model
        
        Returns:
            String response from vision model
        """
        import base64
        
        # Read and encode image
        try:
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to read image {image_path}: {e}")
            raise
        
        # Try OpenRouter models first
        openrouter_models = [
            'google/gemma-3-27b-it:free',
            'mistralai/mistral-small-3.1-24b-instruct:free'
        ]
        
        for model in openrouter_models:
            try:
                logger.info(f"Trying vision model: {model}")
                result = await self._call_openrouter_vision(image_data, prompt, model)
                logger.info(f"Success with {model}")
                return result
            except Exception as e:
                logger.warning(f"Failed with {model}: {e}")
                continue
        
        # Final fallback: Mistral Pixtral
        try:
            logger.info("Trying final fallback: Mistral Pixtral")
            result = await self._call_mistral_vision(image_data, prompt)
            logger.info("Success with Mistral Pixtral")
            return result
        except Exception as e:
            logger.error(f"All vision models failed. Last error: {e}")
            raise Exception("All vision models failed")
    
    async def _call_openrouter_vision(self, image_data, prompt, model):
        """Call OpenRouter vision model"""
        url = 'https://openrouter.ai/api/v1/chat/completions'
        headers = {
            'Authorization': f'Bearer {self.openrouter_key}',
            'HTTP-Referer': 'https://flowmind.local',
            'X-Title': 'FlowMind'
        }
        
        body = {
            'model': model,
            'messages': [{
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': prompt},
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': f'data:image/jpeg;base64,{image_data}'
                        }
                    }
                ]
            }],
            'temperature': 0.3
        }
        
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=body, headers=headers, timeout=90)
            r.raise_for_status()
            return r.json()['choices'][0]['message']['content']
    
    async def _call_mistral_vision(self, image_data, prompt):
        """Call Mistral Pixtral vision model"""
        url = 'https://api.mistral.ai/v1/chat/completions'
        headers = {'Authorization': f'Bearer {self.mistral_key}'}
        
        body = {
            'model': 'pixtral-12b-2409',
            'messages': [{
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': prompt},
                    {
                        'type': 'image_url',
                        'image_url': f'data:image/jpeg;base64,{image_data}'
                    }
                ]
            }],
            'temperature': 0.3
        }
        
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=body, headers=headers, timeout=90)
            r.raise_for_status()
            return r.json()['choices'][0]['message']['content']
