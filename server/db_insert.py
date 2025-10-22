import os
from dotenv import load_dotenv
import psycopg2
import csv

# 1️⃣ .env 파일 불러오기
load_dotenv()

# 2️⃣ DATABASE_URL 환경변수 읽기
DATABASE_URL = os.getenv("DATABASE_URL")

# 3️⃣ DB 연결
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# 4️⃣ CSV 파일 불러오기 (BOM 제거용 utf-8-sig)
csv_path = 'musinsa_ranking.csv'
with open(csv_path, newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    print("🧾 CSV 컬럼명:", reader.fieldnames)  # 실제 헤더 확인용

    inserted = 0
    for row in reader:
        try:
            # 파일 이름만 추출 후 경로 수정
            filename = os.path.basename(row['img_path']).replace('\\', '/')
            new_path = f"C:/kdt/musinsa_images/{filename}"

            # INSERT 실행
            cur.execute("""
                INSERT INTO products (rank, brand, name, price, img_path)
                VALUES (%s, %s, %s, %s, %s)
            """, (row['rank'], row['brand'], row['name'], row['price'], new_path))
            
            inserted += 1

        except Exception as e:
            print(f"❌ 행 삽입 실패 ({row}): {e}")

conn.commit()
cur.close()
conn.close()

print(f"✅ 데이터 삽입 완료 ({inserted}개 행 추가됨)")
