import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import asyncio

# 主站URL
base_url = 'the web url'
INVENTORY_FILE = "inventory.json"

# 获取动态 URL 和名称
def get_dynamic_urls():
    try:
        response = requests.get(f'{base_url}/index.php')
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找符合条件的链接并提取名称
        links = soup.find_all('a', href=True)
        dynamic_urls = []
        for link in links:
            href = link['href']
            if '/index.php?rp=/store/' in href:
                full_url = f"{base_url}{href}" 
                link_text = link.get_text(strip=True)
                if link_text:
                    dynamic_urls.append((full_url, link_text))
        return dynamic_urls
    except Exception as e:
        print(f"请求失败：{str(e)} ({base_url}/index.php)")
        return []

# 爬取页面获取库存信息
def scrape_website(url, link_text):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找包含库存的特定标签
        element = soup.find('div', class_='package-qty')
        if element:
            current_snapshot = element.get_text(strip=True)
            available_qty = int(''.join(filter(str.isdigit, current_snapshot)))
            return {"name": link_text, "stock": available_qty, "url": url}
    except Exception as e:
        print(f"请求失败：{str(e)} ({url})")

# 多线程批量爬取所有动态 URL
def scrape_all_websites():
    dynamic_urls = get_dynamic_urls()
    if not dynamic_urls:
        return []

    results = []
    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = {executor.submit(scrape_website, url, link_text): (url, link_text) for url, link_text in dynamic_urls}
        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as e:
                print(f"爬取发生错误: {e}")
    return results

# 异步更新 JSON 文件的库存信息
async def update_inventory_json():
    loop = asyncio.get_running_loop()
    current_data = await loop.run_in_executor(None, scrape_all_websites)
    if os.path.exists(INVENTORY_FILE):
        with open(INVENTORY_FILE, "r") as f:
            previous_data = json.load(f)
        for item in current_data:
            matching = next((prev for prev in previous_data if prev["name"] == item["name"]), None)
            item["previous_stock"] = matching["stock"] if matching else 0
    with open(INVENTORY_FILE, "w") as f:
        json.dump(current_data, f)
