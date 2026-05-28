import os
import importlib
import httpx
from urllib.parse import urlparse

# Global registry to map domains to their respective bypass functions
HANDLERS = {}

def load_handlers():
    """
    Dynamically imports all python modules inside the handlers package
    and registers their supported domains automatically.
    """
    handlers_dir = os.path.join(os.path.dirname(__file__), "handlers")
    for filename in os.listdir(handlers_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"handlers.{filename[:-3]}"
            module = importlib.import_module(module_name)
            
            if hasattr(module, "DOMAINS") and hasattr(module, "bypass"):
                for domain in module.DOMAINS:
                    HANDLERS[domain.lower()] = module.bypass

# Execute registration on initialization
load_handlers()

async def route_and_bypass(url: str) -> str:
    """
    Parses the domain of the incoming link and directs it to the correct handler script.
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower().replace("www.", "")
    
    # Standard user-agent headers to mimic a normal desktop browser environment
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=25.0) as client:
        # Match domain directly to registered handlers
        if domain in HANDLERS:
            try:
                return await HANDLERS[domain](client, url)
            except Exception as e:
                return f"Error inside execution script for ({domain}): {str(e)}"
        
        # Fallback: If no custom script matches, try basic HTTP redirection tracking
        else:
            try:
                response = await client.get(url)
                if str(response.url) != url:
                    return str(response.url)
                return "No custom handler found for this domain, and no standard HTTP redirection occurred."
            except Exception as e:
                return f"Error during fallback resolution: {str(e)}"