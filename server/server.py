# # main.py
# # main.py
# from fastapi import FastAPI, Depends, HTTPException, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from fastapi.staticfiles import StaticFiles
# import asyncpg, bcrypt, jwt, os
# from datetime import datetime, timedelta
# from dotenv import load_dotenv
# from recommend_test import find_similar_products_by_objects

# # -------------------------
# # 환경 변수 로드
# # -------------------------
# load_dotenv()
# DATABASE_URL = os.getenv("DATABASE_URL")
# JWT_SECRET = os.getenv("JWT_SECRET", "secret-key")
# JWT_ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 120

# app = FastAPI()

# # -------------------------
# # 정적 파일 (이미지 서빙)
# # -------------------------
# IMAGE_DIR = "C:/kdt/musinsa_images"
# if os.path.exists(IMAGE_DIR):
#     app.mount("/static", StaticFiles(directory=IMAGE_DIR), name="static")
#     print(f"✅ Static folder mounted at /static → {IMAGE_DIR}")
# else:
#     print(f"⚠️ 이미지 폴더 경로를 확인하세요: {IMAGE_DIR}")

# # -------------------------
# # CORS 설정
# # -------------------------
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:5173",
#         "http://localhost:3000",
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # -------------------------
# # ✅ DB Connection Pool 생성
# # -------------------------
# @app.on_event("startup")
# async def startup():
#     app.state.db_pool = await asyncpg.create_pool(
#         DATABASE_URL, min_size=1, max_size=10
#     )
#     print("✅ PostgreSQL Connection Pool Created")

# @app.on_event("shutdown")
# async def shutdown():
#     if hasattr(app.state, "db_pool"):
#         await app.state.db_pool.close()
#         print("🛑 PostgreSQL Connection Pool Closed")

# # ✅ FastAPI에서 권장되는 yield 기반 dependency
# async def get_db():
#     async with app.state.db_pool.acquire() as conn:
#         yield conn

# # -------------------------
# # JWT 유틸
# # -------------------------
# def create_access_token(payload: dict, expires_delta: timedelta | None = None):
#     data = payload.copy()
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     data.update({"exp": expire})
#     token = jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)
#     return token

# # -------------------------
# # 인증(쿠키)
# # -------------------------
# async def get_current_user(request: Request):
#     token = request.cookies.get("access_token")
#     if not token:
#         raise HTTPException(status_code=401, detail="토큰이 없습니다.")
#     try:
#         payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
#         return payload
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
#     except jwt.InvalidTokenError:
#         raise HTTPException(status_code=403, detail="유효하지 않은 토큰입니다.")

# # -------------------------
# # 기본 라우트
# # -------------------------
# @app.get("/")
# async def root():
#     return {"message": "FastAPI Server running"}

# @app.get("/api/testdb")
# async def test_db(conn=Depends(get_db)):
#     row = await conn.fetchrow("SELECT NOW() AS now")
#     return {"server_time": row["now"]}

# # -------------------------
# # 회원가입
# # -------------------------
# @app.post("/api/auth/register")
# async def register_user(request: Request, conn=Depends(get_db)):
#     data = await request.json()
#     name = data.get("name"); gender = data.get("gender")
#     birthDate = data.get("birthDate"); user_id = data.get("user_id")
#     password = data.get("password")
#     if not all([name, gender, birthDate, user_id, password]):
#         raise HTTPException(status_code=400, detail="모든 필드를 입력하세요.")
    
#     birthYear = datetime.strptime(birthDate, "%Y-%m-%d").year
#     age = datetime.utcnow().year - birthYear
#     hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

#     try:
#         q = """
#         INSERT INTO users (name, gender, age, user_id, password)
#         VALUES ($1,$2,$3,$4,$5)
#         RETURNING id, name, gender, age, user_id
#         """
#         user = await conn.fetchrow(q, name, gender, age, user_id, hashed_pw)
#         return {"message": "회원가입 성공", "user": dict(user)}
#     except asyncpg.UniqueViolationError:
#         raise HTTPException(status_code=400, detail="이미 사용 중인 아이디입니다.")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # -------------------------
# # 로그인
# # -------------------------
# @app.post("/api/auth/login")
# async def login_user(request: Request, conn=Depends(get_db)):
#     data = await request.json()
#     user_id = data.get("user_id"); password = data.get("password")
#     if not all([user_id, password]):
#         raise HTTPException(status_code=400, detail="모든 필드를 입력하세요.")

#     user = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
#     if not user:
#         raise HTTPException(status_code=400, detail="존재하지 않는 아이디입니다.")
#     if not bcrypt.checkpw(password.encode(), user["password"].encode()):
#         raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다.")

#     payload = {"id": user["id"], "user_id": user["user_id"], "name": user["name"]}
#     token = create_access_token(payload)

#     response = JSONResponse(content={
#         "message": "로그인 성공",
#         "user": {
#             "id": user["id"],
#             "name": user["name"],
#             "gender": user["gender"],
#             "age": user["age"],
#         },
#     })
#     response.set_cookie(
#         key="access_token",
#         value=token,
#         httponly=True,
#         secure=False,
#         samesite="lax",
#         max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
#         path="/",
#     )
#     return response

# # -------------------------
# # 로그아웃
# # -------------------------
# @app.post("/api/auth/logout")
# async def logout_user():
#     response = JSONResponse(content={"message": "로그아웃 완료"})
#     response.delete_cookie("access_token", path="/")
#     return response

# # -------------------------
# # 로그인 상태 확인
# # -------------------------
# @app.get("/api/auth/me")
# async def get_me(user=Depends(get_current_user), conn=Depends(get_db)):
#     rec = await conn.fetchrow(
#         "SELECT id, name, gender, age, user_id FROM users WHERE id = $1",
#         user["id"],
#     )
#     if not rec:
#         raise HTTPException(status_code=404, detail="사용자 없음")
#     return {"user": dict(rec)}

# # -------------------------
# # 🛍️ 상품 목록 조회 API
# # -------------------------

# @app.get("/api/products")
# async def get_products(user=Depends(get_current_user), conn=Depends(get_db)):
#     """
#     상품 리스트 + 로그인한 사용자의 좋아요 상태 포함
#     """
#     try:
#         query = """
#             SELECT 
#                 p.id, 
#                 p.rank, 
#                 p.brand, 
#                 p.name, 
#                 p.price, 
#                 p.img_path,
#                 COALESCE(p.like_count, 0) AS likes,
#                 COALESCE(l.liked, FALSE) AS liked
#             FROM products AS p
#             LEFT JOIN likes AS l
#                 ON p.id = l.product_id 
#                AND l.user_id = $1
#             ORDER BY p.rank ASC
#             LIMIT 30;
#         """
#         rows = await conn.fetch(query, user["id"])

#         products = [
#             {
#                 "id": r["id"],
#                 "rank": r["rank"],
#                 "brand": r["brand"],
#                 "name": r["name"],
#                 "price": float(r["price"]),
#                 "img_path": r["img_path"],
#                 "likes": r["likes"],
#                 "liked": r["liked"],
#             }
#             for r in rows
#         ]
#         return {"products": products}

#     except Exception as e:
#         print(f"❌ [get_products] Error: {e}")
#         raise HTTPException(status_code=500, detail="상품 불러오기 실패")



# @app.get("/api/recommend/{product_id}/{label}")
# async def recommend_by_label(product_id: int, label: str, conn=Depends(get_db)):
#     # 1️⃣ 기준 상품의 특정 라벨 벡터 추출
#     query_vector = await conn.fetchval("""
#         SELECT vector FROM product_items
#         WHERE product_id=$1 AND label=$2
#         ORDER BY confidence DESC LIMIT 1
#     """, product_id, label)

#     if not query_vector:
#         raise HTTPException(status_code=404, detail=f"{label} 벡터 없음")

#     # 2️⃣ 다른 상품의 동일 라벨과 비교
#     rows = await conn.fetch("""
#         SELECT p.id, p.brand, p.name, p.price, p.img_path
#         FROM product_items pi
#         JOIN products p ON p.id = pi.product_id
#         WHERE pi.product_id != $1 AND pi.label = $2
#         ORDER BY pi.vector <-> $3
#         LIMIT 6;
#     """, product_id, label, query_vector)

#     return {"label": label, "recommendations": [dict(r) for r in rows]}



# # ✅ 좋아요 토글 API (최신 버전)
# @app.post("/api/like/{product_id}")
# async def toggle_like(product_id: int, user=Depends(get_current_user), conn=Depends(get_db)):
#     """
#     사용자가 특정 상품에 좋아요를 누르거나 취소함.
#     like 테이블과 products.like_count 동기화.
#     """
#     try:
#         # 현재 사용자 좋아요 상태 확인
#         record = await conn.fetchrow("""
#             SELECT id, liked FROM likes
#             WHERE user_id=$1 AND product_id=$2
#         """, user["id"], product_id)

#         if record:
#             # 이미 좋아요 상태면 토글 (True→False or False→True)
#             new_state = not record["liked"]
#             await conn.execute("""
#                 UPDATE likes SET liked=$1 WHERE id=$2
#             """, new_state, record["id"])
#         else:
#             # 기록이 없으면 새로 삽입
#             new_state = True
#             await conn.execute("""
#                 INSERT INTO likes (user_id, product_id, liked)
#                 VALUES ($1, $2, TRUE)
#             """, user["id"], product_id)

#         # products.like_count 값 갱신
#         if new_state:
#             await conn.execute("""
#                 UPDATE products SET like_count = COALESCE(like_count,0) + 1 WHERE id=$1
#             """, product_id)
#         else:
#             await conn.execute("""
#                 UPDATE products SET like_count = GREATEST(COALESCE(like_count,0) - 1, 0)
#                 WHERE id=$1
#             """, product_id)

#         new_like_count = await conn.fetchval("""
#             SELECT like_count FROM products WHERE id=$1
#         """, product_id)

#         return {"liked": new_state, "new_like_count": new_like_count}

#     except Exception as e:
#         print(f"❌ [toggle_like] Error: {e}")
#         raise HTTPException(status_code=500, detail="좋아요 처리 실패")
    

# @app.post("/api/recommend")
# async def recommend_by_image(request: Request):
#     """
#     사용자가 업로드한 이미지를 기반으로 유사 상품 추천
#     """
#     try:
#         data = await request.json()
#         image_path = data.get("image_path")

#         if not image_path:
#             raise HTTPException(status_code=400, detail="image_path가 필요합니다.")

#         results = await find_similar_products_by_objects(image_path, top_k=6)

#         if not results:
#             return {"message": "추천 결과가 없습니다.", "recommendations": []}

#         return {"message": "추천 성공", "recommendations": results}

#     except Exception as e:
#         print(f"❌ [recommend_by_image] Error: {e}")
#         raise HTTPException(status_code=500, detail="추천 처리 중 오류 발생")



# main.py
from fastapi import FastAPI, Depends, HTTPException, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import asyncpg, bcrypt, jwt, os, torch, numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI
from gradio_client import Client, handle_file
import tempfile
import shutil
import requests
from pathlib import Path
from recommend_test import (
    load_detection_model,
    load_embedding_model,
    detect_objects,
    get_object_embeddings,
    load_image,
    find_similar_products_by_objects,
)

# -------------------------
# 환경 변수 로드
# -------------------------
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET", "secret-key")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120
client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
# -------------------------
# 앱 초기화
# -------------------------
app = FastAPI()

# -------------------------
# 정적 파일 (이미지 서빙)
# -------------------------

BASE_STATIC_DIR = "C:/kdt/server/static"

# 상품 이미지 폴더
IMAGE_DIR = "C:/kdt/musinsa_images"
if os.path.exists(IMAGE_DIR):
    app.mount("/static/images", StaticFiles(directory=IMAGE_DIR), name="images")
    print(f"✅ 상품 이미지 폴더 등록 → /static/images → {IMAGE_DIR}")

# 결과 이미지 폴더
RESULT_DIR = "C:/kdt/server/static/results"
if os.path.exists(RESULT_DIR):
    app.mount("/static/results", StaticFiles(directory=RESULT_DIR), name="results")
    print(f"✅ 결과 이미지 폴더 등록 → /static/results → {RESULT_DIR}")


# -------------------------
# CORS 설정
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# ✅ DB Connection Pool
# -------------------------
@app.on_event("startup")
async def startup():
    app.state.db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
    print("✅ PostgreSQL Connection Pool Created")

@app.on_event("shutdown")
async def shutdown():
    if hasattr(app.state, "db_pool"):
        await app.state.db_pool.close()
        print("🛑 PostgreSQL Connection Pool Closed")

async def get_db():
    async with app.state.db_pool.acquire() as conn:
        yield conn

# -------------------------
# JWT 유틸
# -------------------------
def create_access_token(payload: dict, expires_delta: timedelta | None = None):
    data = payload.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    data.update({"exp": expire})
    return jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="토큰이 없습니다.")
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="유효하지 않은 토큰입니다.")

# -------------------------
# 기본 라우트
# -------------------------
@app.get("/")
async def root():
    return {"message": "FastAPI Server running"}

@app.get("/api/testdb")
async def test_db(conn=Depends(get_db)):
    row = await conn.fetchrow("SELECT NOW() AS now")
    return {"server_time": row["now"]}

# -------------------------
# 회원가입 / 로그인 / 로그아웃 / 상태확인
# -------------------------
@app.post("/api/auth/register")
async def register_user(request: Request, conn=Depends(get_db)):
    data = await request.json()
    name, gender, birthDate, user_id, password = (
        data.get("name"),
        data.get("gender"),
        data.get("birthDate"),
        data.get("user_id"),
        data.get("password"),
    )
    if not all([name, gender, birthDate, user_id, password]):
        raise HTTPException(status_code=400, detail="모든 필드를 입력하세요.")
    birthYear = datetime.strptime(birthDate, "%Y-%m-%d").year
    age = datetime.utcnow().year - birthYear
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        q = """
        INSERT INTO users (name, gender, age, user_id, password)
        VALUES ($1,$2,$3,$4,$5)
        RETURNING id, name, gender, age, user_id
        """
        user = await conn.fetchrow(q, name, gender, age, user_id, hashed_pw)
        return {"message": "회원가입 성공", "user": dict(user)}
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=400, detail="이미 사용 중인 아이디입니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login")
async def login_user(request: Request, conn=Depends(get_db)):
    data = await request.json()
    user_id, password = data.get("user_id"), data.get("password")
    if not all([user_id, password]):
        raise HTTPException(status_code=400, detail="모든 필드를 입력하세요.")
    user = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
    if not user:
        raise HTTPException(status_code=400, detail="존재하지 않는 아이디입니다.")
    if not bcrypt.checkpw(password.encode(), user["password"].encode()):
        raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다.")
    payload = {"id": user["id"], "user_id": user["user_id"], "name": user["name"]}
    token = create_access_token(payload)
    response = JSONResponse(
        content={
            "message": "로그인 성공",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "gender": user["gender"],
                "age": user["age"],
            },
        }
    )
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    return response

@app.post("/api/auth/logout")
async def logout_user():
    response = JSONResponse(content={"message": "로그아웃 완료"})
    response.delete_cookie("access_token", path="/")
    return response

@app.get("/api/auth/me")
async def get_me(user=Depends(get_current_user), conn=Depends(get_db)):
    rec = await conn.fetchrow(
        "SELECT id, name, gender, age, user_id FROM users WHERE id = $1",
        user["id"],
    )
    if not rec:
        raise HTTPException(status_code=404, detail="사용자 없음")
    return {"user": dict(rec)}

# -------------------------
# 상품 목록
# -------------------------
@app.get("/api/products")
async def get_products(user=Depends(get_current_user), conn=Depends(get_db)):
    try:
        query = """
            SELECT 
                p.id, p.rank, p.brand, p.name, p.price, p.img_path,
                COALESCE(p.like_count, 0) AS likes,
                COALESCE(l.liked, FALSE) AS liked
            FROM products AS p
            LEFT JOIN likes AS l
                ON p.id = l.product_id AND l.user_id = $1
            ORDER BY p.rank ASC
            LIMIT 30;
        """
        rows = await conn.fetch(query, user["id"])
        products = [
            {
                "id": r["id"],
                "rank": r["rank"],
                "brand": r["brand"],
                "name": r["name"],
                "price": float(r["price"]),
                "img_path": r["img_path"],
                "likes": r["likes"],
                "liked": r["liked"],
            }
            for r in rows
        ]
        return {"products": products}
    except Exception as e:
        print(f"❌ [get_products] Error: {e}")
        raise HTTPException(status_code=500, detail="상품 불러오기 실패")

# -------------------------
# 좋아요
# -------------------------
@app.post("/api/like/{product_id}")
async def toggle_like(product_id: int, user=Depends(get_current_user), conn=Depends(get_db)):
    try:
        record = await conn.fetchrow(
            "SELECT id, liked FROM likes WHERE user_id=$1 AND product_id=$2",
            user["id"], product_id,
        )
        if record:
            new_state = not record["liked"]
            await conn.execute("UPDATE likes SET liked=$1 WHERE id=$2", new_state, record["id"])
        else:
            new_state = True
            await conn.execute("INSERT INTO likes (user_id, product_id, liked) VALUES ($1,$2,TRUE)", user["id"], product_id)
        if new_state:
            await conn.execute("UPDATE products SET like_count = COALESCE(like_count,0)+1 WHERE id=$1", product_id)
        else:
            await conn.execute("UPDATE products SET like_count = GREATEST(COALESCE(like_count,0)-1,0) WHERE id=$1", product_id)
        count = await conn.fetchval("SELECT like_count FROM products WHERE id=$1", product_id)
        return {"liked": new_state, "new_like_count": count}
    except Exception as e:
        print(f"❌ [toggle_like] Error: {e}")
        raise HTTPException(status_code=500, detail="좋아요 처리 실패")

# -------------------------
# 🎯 하이브리드 추천 API (이미지 0.4 + 텍스트 0.6)
# -------------------------
emb_proc, emb_model = load_embedding_model()
@app.post("/api/recommend_hybrid")
async def recommend_hybrid(
    file: UploadFile | None = File(None),
    text_prompt: str = Form(""),
    conn=Depends(get_db),
):
    """
    이미지 + 텍스트 임베딩을 결합하여 유사도 계산
    """

    # ✅ 요청 데이터 확인 로그
    print("===============================================", flush=True)
    print("📨 받은 text_prompt =", repr(text_prompt), flush=True)
    print("📦 받은 file =", file.filename if file else "없음", flush=True)
    print("===============================================", flush=True)

    try:
        image_vec, text_vec = None, None

        # ✅ 이미지 임베딩 생성
        if file:
            print("🖼️ 이미지 임베딩 생성 시작", flush=True)
            file_path = f"C:/kdt/uploads/{datetime.now().timestamp()}_{file.filename}"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(await file.read())

            det_proc, det_model = load_detection_model()
            img = load_image(file_path)
            det = detect_objects(img, det_proc, det_model)
            emb = get_object_embeddings(img, det, det_model, emb_proc, emb_model)

            if emb:
                image_vec = np.mean(list(emb.values()), axis=0).astype("float32")
                image_vec = image_vec / np.linalg.norm(image_vec)
                print("✅ 이미지 임베딩 생성 완료", flush=True)
            else:
                print("⚠️ 이미지에서 객체 임베딩을 찾지 못함", flush=True)

        # ✅ 텍스트 임베딩 (LLM 정제)
        if text_prompt.strip():
            print("🚀 LLM 호출 시작 ==============================", flush=True)
            print(f"🧠 LLM 원문 입력: {text_prompt}", flush=True)

            prompt = f"""
                너는 패션 상품 검색 엔진의 텍스트 필터링 도우미야.
                사용자의 문장을 실제 상품명과 유사한 형태로 바꿔.
                출력은 오직 짧은 키워드 문장(상품명)만 포함해야 해.
                다른 말이나 설명, 인사말은 절대 쓰지 마.
                다음 규칙을 지켜:
                - 가능한 한 짧게 (3~7단어)
                - 색상, 스타일, 아이템명을 반드시 포함해
                - 인구학적 정보(20대, 남성, 여성)는 단어 1개로 요약해 포함해
                - 예시:
                입력: "20대 남성이 입기 좋은 깔끔한 데일리룩"
                출력: "20대 남성 화이트 미니멀 셋업 수트"
            입력: "{text_prompt}"
            출력:

            """

            try:
                print("📡 OpenAI API 요청 보내는 중...", flush=True)
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                )
                print("✅ OpenAI 응답 수신 완료", flush=True)

                cleaned = resp.choices[0].message.content.strip()
                print(f"🧠 LLM 정제 결과: {cleaned}", flush=True)

                text_inputs = emb_proc(text=[cleaned], return_tensors="pt")
                with torch.no_grad():
                    text_vec = emb_model.get_text_features(**text_inputs).squeeze().numpy().astype("float32")
                    text_vec = text_vec / np.linalg.norm(text_vec)
                print("✅ 텍스트 임베딩 생성 완료", flush=True)

            except Exception as e:
                print(f"❌ LLM 호출 중 오류 발생: {e}", flush=True)
                raise HTTPException(status_code=500, detail=f"LLM 호출 실패: {e}")

            print("================================================", flush=True)

        # ✅ 입력 데이터가 전혀 없을 때
        if image_vec is None and text_vec is None:
            raise HTTPException(status_code=400, detail="이미지 또는 텍스트가 필요합니다.")

        # ✅ 유사도 계산 쿼리
        print("🔍 유사도 계산 시작", flush=True)
        if image_vec is not None and text_vec is not None:
            query = """
                SELECT p.id, p.name, p.brand, p.price, p.img_path,
                       (0.7 * (1 - (v.image_vector <=> $1)) +
                        0.3 * (1 - (p.name_vector <=> $2))) AS hybrid_similarity
                FROM products p
                JOIN product_vectors v ON p.id = v.product_id
                ORDER BY hybrid_similarity DESC
                LIMIT 6;
            """
            rows = await conn.fetch(
                query,
                "[" + ",".join(map(str, image_vec.tolist())) + "]",
                "[" + ",".join(map(str, text_vec.tolist())) + "]"
            )
        elif image_vec is not None:
            query = """
                SELECT p.id, p.name, p.brand, p.price, p.img_path,
                       1 - (v.image_vector <=> $1) AS hybrid_similarity
                FROM products p
                JOIN product_vectors v ON p.id = v.product_id
                ORDER BY hybrid_similarity DESC
                LIMIT 6;
            """
            rows = await conn.fetch(
                query,
                "[" + ",".join(map(str, image_vec.tolist())) + "]"
            )
        else:
            query = """
                SELECT p.id, p.name, p.brand, p.price, p.img_path,
                       1 - (p.name_vector <=> $1) AS hybrid_similarity
                FROM products p
                ORDER BY hybrid_similarity DESC
                LIMIT 6;
            """
            rows = await conn.fetch(
                query,
                "[" + ",".join(map(str, text_vec.tolist())) + "]"
            )

        print(f"✅ 추천 완료, 결과 {len(rows)}개", flush=True)
        print("===============================================", flush=True)

        return {"recommendations": [dict(r) for r in rows]}

    except Exception as e:
        print(f"❌ [recommend_hybrid] Error: {e}", flush=True)
        raise HTTPException(status_code=500, detail=f"추천 실패: {e}")

@app.post("/api/fitting")
async def fitting(
    vton_img: UploadFile = File(...),
    garm_img_path: str = Form(...),
    category: str = Form("Upper-body")
):
    try:
        # ✅ 임시 저장된 유저 이미지
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_user:
            temp_user.write(await vton_img.read())
            temp_user_path = temp_user.name

        garm_full_path = os.path.join("C:/kdt/musinsa_images", os.path.basename(garm_img_path))
        client = Client("levihsu/OOTDiffusion")

        result = client.predict(
            vton_img=handle_file(temp_user_path),
            garm_img=handle_file(garm_full_path),
            category=category,
            n_samples=1,
            n_steps=20,
            image_scale=2,
            seed=-1,
            api_name="/process_dc"
        )

        # ✅ HuggingFace 결과 구조: [{'image': '로컬경로', 'caption': None}]
        output_path = result[0]["image"]

        # ✅ 결과 이미지를 static 폴더로 복사
        static_dir = Path("C:/kdt/server/static/results")
        static_dir.mkdir(parents=True, exist_ok=True)

        # ✅ 결과 이미지를 static/results 폴더에 저장
        filename = f"fitting_{datetime.now().timestamp()}.jpg"
        save_path = Path(RESULT_DIR) / filename
        shutil.copy(output_path, save_path)

        # ✅ URL 반환
        result_url = f"http://localhost:8000/static/results/{filename}"
        print("✅ 결과 URL:", result_url)
        return JSONResponse({"result_url": result_url})

    except Exception as e:
        print(f"❌ [fitting] Error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)
    
# ✅ 날씨 정보 가져오기 함수
def get_weather(city="Seoul"):
    try:
        url = (
            f"http://api.openweathermap.org/data/2.5/weather?"
            f"q={city}&appid={WEATHER_API_KEY}&units=metric&lang=kr"
        )
        res = requests.get(url).json()
        temp = res["main"]["temp"]
        desc = res["weather"][0]["description"]
        return {"temp": temp, "desc": desc}
    except Exception:
        return {"temp": None, "desc": "날씨 정보를 불러올 수 없습니다."}


# ✅ 패션 상담 챗봇
@app.post("/api/fashionchat")
async def fashion_chat(request: Request):
    data = await request.json()
    user_input = data.get("message")
    city = data.get("city", "Seoul")

    # 🔹 현재 날씨 정보
    weather = get_weather(city)
    weather_text = f"{city}의 현재 날씨는 {weather['desc']}이며 {weather['temp']}도입니다."

    # 🔹 프롬프트 생성
    prompt = f"""
    당신은 패션 스타일링 전문가입니다.
    사용자의 상황과 현재 날씨를 기반으로 오늘 입기 좋은 옷차림을 추천하세요.
    답변은 간결하고 자연스럽게, 3~4문장 이내로 작성하세요.
    예시로 특정 아이템 조합(상의, 하의, 신발, 색상 등)을 구체적으로 제시하세요.

    현재 날씨: {weather_text}
    사용자 입력: "{user_input}"

    출력 형식 예시:
    - 추천 코디: 그레이 수트, 흰 셔츠, 블랙 구두
    - 코멘트: 결혼식에는 단정하고 포멀한 느낌의 조합이 잘 어울립니다.
    """

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    reply = completion.choices[0].message.content.strip()
    return {"response": reply, "weather": weather_text}