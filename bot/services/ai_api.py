import asyncio
import httpx
from bot.config import NANO_BANANA_API_KEY, NANO_BANANA_URL, KIE_STATUS_URL

async def create_nano_banana_task(prompt: str, image_url: str = None) -> str:
    headers = {
        "Authorization": f"Bearer {NANO_BANANA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    image_input = [image_url] if image_url else []

    payload = {
        "model": "nano-banana-2",
        "input": {
            "prompt": prompt,
            "image_input": image_input,
            "aspect_ratio": "auto",
            "resolution": "1K",
            "output_format": "png"
        }
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(NANO_BANANA_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("taskId") or data.get("id")
        else:
            raise Exception(f"Ошибка Kie AI: {response.status_code} - {response.text}")


async def wait_for_completion(task_id: str, max_attempts: int = 20, delay: int = 2) -> str:
    headers = {
        "Authorization": f"Bearer {NANO_BANANA_API_KEY}"
    }
    params = {"taskId": task_id}

    async with httpx.AsyncClient(timeout=30.0) as client:
        for _ in range(max_attempts):
            response = await client.get(KIE_STATUS_URL, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                state = data.get("state") or data.get("status")
                
                if state == "SUCCESS":
                    results = data.get("result", {})
                    image_list = results.get("image_urls", [])
                    if image_list:
                        return image_list[0]
                    return data.get("outputUrl")
                
                elif state in ["FAIL", "FAILED"]:
                    raise Exception("Нейросеть не смогла сгенерировать изображение.")
            
            await asyncio.sleep(delay)
            
    raise Exception("Превышено время ожидания ответа от нейросети.")