# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# import time
# import os
# import requests
# import csv

# # ===================== 저장 폴더 설정 =====================
# IMAGE_DIR = "musinsa_images"
# os.makedirs(IMAGE_DIR, exist_ok=True)
# CSV_FILE = "musinsa_ranking.csv"

# # ===================== 크롬 옵션 설정 =====================
# chrome_options = Options()
# # chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")

# service = Service("C:\\study25\\tf114\\chromedriver-win64\\chromedriver.exe")
# driver = webdriver.Chrome(service=service, options=chrome_options)

# # ===================== 페이지 접속 =====================
# url = "https://www.musinsa.com/main/musinsa/ranking?storeCode=musinsa&sectionId=200&contentsId=&categoryCode=001000&subPan=product"
# driver.get(url)
# time.sleep(3)

# # ===================== 스크롤 + 상품 수집 =====================
# SCROLL_STEP = 500           # 한 번에 스크롤할 픽셀
# SCROLL_PAUSE_TIME = 1.5     # 스크롤 후 대기 시간
# collected_ids = set()
# data_list = []

# last_scroll = 0
# while True:
#     # 화면에 보이는 모든 상품 요소
#     items = driver.find_elements(By.CSS_SELECTOR, 'div[data-item-id]')
    
#     for item in items:
#         try:
#             item_id = item.get_attribute("data-item-id")
#             if item_id in collected_ids:
#                 continue
#             collected_ids.add(item_id)

#             # StaleElement 대비 재시도
#             for _ in range(3):
#                 try:
#                     rank = item.get_attribute("data-item-list-index")
#                     brand = item.get_attribute("data-item-brand")
#                     name = item.find_element(By.CSS_SELECTOR, 'p[class*="line-clamp-2"]').text
#                     price = item.get_attribute("data-price")
#                     img_url = item.find_element(By.CSS_SELECTOR, 'img').get_attribute("src")
#                     break
#                 except:
#                     time.sleep(0.5)

#             # 이미지 저장
#             img_filename = f"{rank}_{name.replace('/', '_').replace(' ', '_')}.jpg"
#             img_path = os.path.join(IMAGE_DIR, img_filename)
#             try:
#                 img_data = requests.get(img_url).content
#                 with open(img_path, "wb") as f:
#                     f.write(img_data)
#             except:
#                 img_path = ""
            
#             data_list.append({
#                 "rank": rank,
#                 "brand": brand,
#                 "name": name,
#                 "price": price,
#                 "img_path": img_path
#             })
#         except Exception as e:
#             print(f"상품 추출 실패: {e}")

#     # 화면을 조금씩 스크롤
#     driver.execute_script(f"window.scrollBy(0, {SCROLL_STEP});")
#     time.sleep(SCROLL_PAUSE_TIME)
    
#     new_scroll = driver.execute_script("return window.scrollY + window.innerHeight")
#     page_height = driver.execute_script("return document.body.scrollHeight")
    
#     if new_scroll >= page_height:
#         break

# # ===================== CSV 저장 =====================
# with open(CSV_FILE, "w", newline="", encoding="utf-8-sig") as f:
#     writer = csv.DictWriter(f, fieldnames=["rank", "brand", "name", "price", "img_path"])
#     writer.writeheader()
#     writer.writerows(data_list)

# print(f"총 {len(data_list)}개 상품 수집 완료!")
# driver.quit()
from prometheus_client import start_http_server, Counter, Summary, Gauge
import time
import os
import csv
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# ===================== Prometheus Metrics 정의 =====================
# 1. 총 크롤링 개수
CRAWL_TOTAL = Counter("musinsa_crawl_total", "총 크롤링된 상품 수")

# 2. 성공 / 실패 ratio
CRAWL_SUCCESS = Counter("musinsa_crawl_success_total", "성공한 크롤링 수")
CRAWL_FAILURE = Counter("musinsa_crawl_failure_total", "실패한 크롤링 수")

# 3. 평균 개당 크롤링 시간
CRAWL_TIME = Summary("musinsa_crawl_item_seconds", "개당 크롤링 시간 (초)")

# 4~5. 도메인별 (혹은 브랜드별) 통계
DOMAIN_TOTAL = Counter("musinsa_domain_total", "도메인별 크롤링 개수", ["brand"])
DOMAIN_SUCCESS = Counter("musinsa_domain_success_total", "도메인별 성공", ["brand"])
DOMAIN_FAILURE = Counter("musinsa_domain_failure_total", "도메인별 실패", ["brand"])

# Prometheus HTTP exporter 시작 (기본 포트 8001)
start_http_server(8001)
print("✅ Prometheus metrics available at http://localhost:8001/metrics")

# ===================== 기존 코드 =====================
IMAGE_DIR = "musinsa_images2"
os.makedirs(IMAGE_DIR, exist_ok=True)
CSV_FILE = "musinsa_ranking2.csv"

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--headless")

service = Service("C:\\kdt\\server\\chromedriver-win64\\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

url = "https://www.musinsa.com/main/musinsa/ranking?storeCode=musinsa&sectionId=200&contentsId=&categoryCode=001000&subPan=product"
driver.get(url)
time.sleep(3)

SCROLL_STEP = 500
SCROLL_PAUSE_TIME = 1.5
collected_ids = set()
data_list = []

while True:
    items = driver.find_elements(By.CSS_SELECTOR, 'div[data-item-id]')
    
    for item in items:
        start_time = time.time()
        try:
            item_id = item.get_attribute("data-item-id")
            if item_id in collected_ids:
                continue
            collected_ids.add(item_id)

            rank = item.get_attribute("data-item-list-index")
            brand = item.get_attribute("data-item-brand")
            name = item.find_element(By.CSS_SELECTOR, 'p[class*="line-clamp-2"]').text
            price = item.get_attribute("data-price")
            img_url = item.find_element(By.CSS_SELECTOR, 'img').get_attribute("src")

            # 이미지 저장
            img_filename = f"{rank}_{name.replace('/', '_').replace(' ', '_')}.jpg"
            img_path = os.path.join(IMAGE_DIR, img_filename)
            img_data = requests.get(img_url).content
            with open(img_path, "wb") as f:
                f.write(img_data)

            data_list.append({
                "rank": rank,
                "brand": brand,
                "name": name,
                "price": price,
                "img_path": img_path
            })

            # ---- Prometheus 기록 ----
            elapsed = time.time() - start_time
            CRAWL_TOTAL.inc()
            CRAWL_SUCCESS.inc()
            DOMAIN_TOTAL.labels(brand=brand).inc()
            DOMAIN_SUCCESS.labels(brand=brand).inc()
            CRAWL_TIME.observe(elapsed)

        except Exception as e:
            CRAWL_FAILURE.inc()
            DOMAIN_FAILURE.labels(brand=brand if 'brand' in locals() else "unknown").inc()
            print(f"상품 추출 실패: {e}")

    driver.execute_script(f"window.scrollBy(0, {SCROLL_STEP});")
    time.sleep(SCROLL_PAUSE_TIME)
    new_scroll = driver.execute_script("return window.scrollY + window.innerHeight")
    page_height = driver.execute_script("return document.body.scrollHeight")
    if new_scroll >= page_height:
        break

with open(CSV_FILE, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["rank", "brand", "name", "price", "img_path"])
    writer.writeheader()
    writer.writerows(data_list)

print(f"총 {len(data_list)}개 상품 수집 완료!")
driver.quit()

# ✅ 크롤링 끝난 뒤에도 /metrics 계속 유지
print("✅ 크롤링 완료! Prometheus /metrics 계속 노출 중 (Ctrl+C로 종료)")
try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    print("🛑 수동 종료됨. Prometheus 서버 중단.")