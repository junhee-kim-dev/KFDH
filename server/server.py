# # main.py
# from fastapi import FastAPI, Depends, HTTPException, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# import asyncpg, bcrypt, jwt, os
# from datetime import datetime, timedelta
# from dotenv import load_dotenv

# load_dotenv()
# DATABASE_URL = os.getenv("DATABASE_URL")
# JWT_SECRET = os.getenv("JWT_SECRET", "secret-key")
# JWT_ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 120  # 2 hours

# app = FastAPI()

# # CORS: 프론트 주소 명시 + allow_credentials True 필수 (쿠키 전송 허용)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:5173",  # 프론트 개발 주소(예시). 실제 도메인으로 수정하세요.
#         "http://localhost:3000",
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # DB 연결관리
# @app.on_event("startup")
# async def startup():
#     app.state.db = await asyncpg.connect(DATABASE_URL)
#     print("✅ PostgreSQL Connected")

# @app.on_event("shutdown")
# async def shutdown():
#     if hasattr(app.state, "db"):
#         await app.state.db.close()
#         print("🛑 PostgreSQL Connection Closed")

# async def get_db():
#     return app.state.db

# # -------------------------
# # 유틸: 토큰 생성
# # -------------------------
# def create_access_token(payload: dict, expires_delta: timedelta | None = None):
#     data = payload.copy()
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     data.update({"exp": expire})
#     token = jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)
#     return token

# # -------------------------
# # 인증(쿠키) 의존성
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
# async def test_db():
#     conn = await get_db()
#     row = await conn.fetchrow("SELECT NOW() AS now")
#     return {"server_time": row["now"]}

# # -------------------------
# # 회원가입 (unchanged)
# # -------------------------
# @app.post("/api/auth/register")
# async def register_user(request: Request):
#     data = await request.json()
#     name = data.get("name"); gender = data.get("gender")
#     birthDate = data.get("birthDate"); user_id = data.get("user_id")
#     password = data.get("password")
#     if not all([name, gender, birthDate, user_id, password]):
#         raise HTTPException(status_code=400, detail="모든 필드를 입력하세요.")
#     birthYear = datetime.strptime(birthDate, "%Y-%m-%d").year
#     age = datetime.utcnow().year - birthYear
#     hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

#     conn = await get_db()
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
# # 로그인: 쿠키로 JWT 발급
# # -------------------------
# @app.post("/api/auth/login")
# async def login_user(request: Request):
#     data = await request.json()
#     user_id = data.get("user_id"); password = data.get("password")
#     if not all([user_id, password]):
#         raise HTTPException(status_code=400, detail="모든 필드를 입력하세요.")
#     conn = await get_db()
#     user = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
#     if not user:
#         raise HTTPException(status_code=400, detail="존재하지 않는 아이디입니다.")
#     if not bcrypt.checkpw(password.encode(), user["password"].encode()):
#         raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다.")

#     # 토큰 생성 (payload에는 최소한의 정보만)
#     payload = {"id": user["id"], "user_id": user["user_id"], "name": user["name"]}
#     token = create_access_token(payload, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

#     # 응답을 JSONResponse로 만들고 쿠키에 토큰 설정
#     response = JSONResponse(content={
#         "message": "로그인 성공",
#         "user": {"id": user["id"], "name": user["name"], "gender": user["gender"], "age": user["age"]},
#     })

#     # 쿠키 옵션
#     # - httponly=True : JS에서 접근 불가 (XSS 방지)
#     # - secure=True : HTTPS에서만 전송 (운영에서 켜기)
#     # - samesite="lax" : CSRF 완화(상황에 따라 'strict'/'none' 조정)
#     # - path="/" : 모든 요청에 대해 전송
#     response.set_cookie(
#         key="access_token",
#         value=token,
#         httponly=True,
#         secure=False,           # 개발(localhost)에서는 False. 배포시 True로 변경하세요.
#         samesite="lax",
#         max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
#         path="/"
#     )
#     return response

# # -------------------------
# # 로그아웃: 쿠키 삭제
# # -------------------------
# @app.post("/api/auth/logout")
# async def logout_user():
#     response = JSONResponse(content={"message": "로그아웃 완료"})
#     response.delete_cookie("access_token", path="/")
#     return response

# # -------------------------
# # 로그인 상태 확인 (쿠키에서 토큰 읽기)
# # -------------------------
# @app.get("/api/auth/me")
# async def get_me(user=Depends(get_current_user)):
#     # get_current_user가 payload를 반환. payload의 id로 DB에서 상세 조회
#     conn = await get_db()
#     rec = await conn.fetchrow("SELECT id, name, gender, age, user_id FROM users WHERE id = $1", user["id"])
#     if not rec:
#         raise HTTPException(status_code=404, detail="사용자 없음")
#     return {"user": dict(rec)}


# main.py
# main.py
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import asyncpg, bcrypt, jwt, os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# -------------------------
# 환경 변수 로드
# -------------------------
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET", "secret-key")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

app = FastAPI()

# -------------------------
# 정적 파일 (이미지 서빙)
# -------------------------
IMAGE_DIR = "C:/kdt/musinsa_images"
if os.path.exists(IMAGE_DIR):
    app.mount("/static", StaticFiles(directory=IMAGE_DIR), name="static")
    print(f"✅ Static folder mounted at /static → {IMAGE_DIR}")
else:
    print(f"⚠️ 이미지 폴더 경로를 확인하세요: {IMAGE_DIR}")

# -------------------------
# CORS 설정
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# ✅ DB Connection Pool 생성
# -------------------------
@app.on_event("startup")
async def startup():
    app.state.db_pool = await asyncpg.create_pool(
        DATABASE_URL, min_size=1, max_size=10
    )
    print("✅ PostgreSQL Connection Pool Created")

@app.on_event("shutdown")
async def shutdown():
    if hasattr(app.state, "db_pool"):
        await app.state.db_pool.close()
        print("🛑 PostgreSQL Connection Pool Closed")

# ✅ FastAPI에서 권장되는 yield 기반 dependency
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
    token = jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

# -------------------------
# 인증(쿠키)
# -------------------------
async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="토큰이 없습니다.")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
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
# 회원가입
# -------------------------
@app.post("/api/auth/register")
async def register_user(request: Request, conn=Depends(get_db)):
    data = await request.json()
    name = data.get("name"); gender = data.get("gender")
    birthDate = data.get("birthDate"); user_id = data.get("user_id")
    password = data.get("password")
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

# -------------------------
# 로그인
# -------------------------
@app.post("/api/auth/login")
async def login_user(request: Request, conn=Depends(get_db)):
    data = await request.json()
    user_id = data.get("user_id"); password = data.get("password")
    if not all([user_id, password]):
        raise HTTPException(status_code=400, detail="모든 필드를 입력하세요.")

    user = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
    if not user:
        raise HTTPException(status_code=400, detail="존재하지 않는 아이디입니다.")
    if not bcrypt.checkpw(password.encode(), user["password"].encode()):
        raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다.")

    payload = {"id": user["id"], "user_id": user["user_id"], "name": user["name"]}
    token = create_access_token(payload)

    response = JSONResponse(content={
        "message": "로그인 성공",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "gender": user["gender"],
            "age": user["age"],
        },
    })
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

# -------------------------
# 로그아웃
# -------------------------
@app.post("/api/auth/logout")
async def logout_user():
    response = JSONResponse(content={"message": "로그아웃 완료"})
    response.delete_cookie("access_token", path="/")
    return response

# -------------------------
# 로그인 상태 확인
# -------------------------
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
# 🛍️ 상품 목록 조회 API
# -------------------------
@app.get("/api/products")
async def get_products(conn=Depends(get_db)):
    try:
        rows = await conn.fetch("""
            SELECT rank, brand, name, price, img_path, COALESCE(like_count, 0) AS likes
            FROM products
            ORDER BY rank ASC
            LIMIT 30;
        """)
        products = [
            {
                "rank": r["rank"],
                "brand": r["brand"],
                "name": r["name"],
                "price": float(r["price"]),
                "img_path": r["img_path"],
                "likes": r["likes"],
            }
            for r in rows
        ]
        return {"products": products}

    except Exception as e:
        print(f"❌ [get_products] DB Error: {e}")
        raise HTTPException(status_code=500, detail="상품 데이터를 불러오는 중 오류가 발생했습니다.")

