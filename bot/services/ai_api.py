import json
import httpx
import asyncio

from bot.config import config

async def create_nano_banana_task(prompt: str, image_url: str = None) -> str:
    headers = {
        "Authorization": f"Bearer {config.NANO_BANANA_API_KEY}",
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
        response = await client.post(config.NANO_BANANA_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            json_response = response.json()
            print("ОТВЕТ ОТ KIE AI ПРИ СОЗДАНИИ ЗАДАЧИ:", json_response)
            
            api_code = json_response.get("code")
            if api_code == 402:
                raise Exception("Закончились кредиты в Kie AI. Пожалуйста, пополни баланс API (на сайте нейросети).")
            elif api_code not in (200, None):
                error_msg = json_response.get("msg", "Неизвестная ошибка")
                raise Exception(f"Ошибка API Kie AI: {error_msg}")
            
            inner_data = json_response.get("data") or {} 
            task_id = inner_data.get("taskId") or json_response.get("taskId") or json_response.get("id")
            
            if not task_id:
                raise Exception(f"Нейросеть не вернула ID! Структура ответа: {json_response}")
                
            return str(task_id)
            
        else:
            raise Exception(f"Ошибка HTTP запроса Kie AI: {response.status_code} - {response.text}")


async def wait_for_completion(task_id: str, max_attempts: int = 120, delay: int = 3) -> str:
    headers = {
        "Authorization": f"Bearer {config.NANO_BANANA_API_KEY}"
    }
    params = {"taskId": task_id}

    async with httpx.AsyncClient(timeout=30.0) as client:
        for attempt in range(max_attempts):
            await asyncio.sleep(delay)
            
            response = await client.get(config.KIE_STATUS_URL, params=params, headers=headers)
            
            if response.status_code == 200:
                res_json = response.json()
                
                data = res_json.get("data") if isinstance(res_json.get("data"), dict) else res_json
                raw_state = data.get("state") or data.get("status") or res_json.get("state") or ""
                state = str(raw_state).upper()

                print(f"Попытка {attempt + 1}: Статус задачи = '{state}'")
                
                if state in ["SUCCESS", "COMPLETED", "DONE"]:
                    result_json_str = data.get("resultJson")
                    if result_json_str:
                        import json
                        try:
                            parsed_data = json.loads(result_json_str)
                            result_urls = parsed_data.get("resultUrls", [])
                            if result_urls:
                                return result_urls[0]
                        except json.JSONDecodeError:
                            print("Ошибка: не удалось распарсить resultJson")

                    results = data.get("result") or res_json.get("result") or {}
                    
                    if isinstance(results, dict):
                        urls = results.get("urls") or results.get("image_urls") or []
                        if urls:
                            return urls[0]
                    elif isinstance(results, str):
                        return results
                        
                    url = data.get("resultUrl") or data.get("outputUrl") or res_json.get("resultUrl")
                    if url:
                        return url
                        
                    raise Exception(f"Статус SUCCESS, но URL не найден. Ответ: {res_json}")
                
                elif state in ["FAIL", "FAILED", "ERROR"]:
                    print("ДЕТАЛИ ОШИБКИ ОТ KIE AI:", res_json)
                    fail_reason = (
                        data.get("failReason") 
                        or data.get("msg") 
                        or res_json.get("msg") 
                        or "Неизвестная ошибка"
                    )
                    raise Exception(f"Нейросеть не смогла сгенерировать изображение: {fail_reason}")
            
            else:
                print(f"Попытка {attempt + 1}: Ошибка проверки статуса {response.status_code}")
                if response.status_code == 404:
                    raise Exception("Ошибка 404: Неверный KIE_STATUS_URL!")
            
    raise Exception("Превышено время ожидания ответа от нейросети.")