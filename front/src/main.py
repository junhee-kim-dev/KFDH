from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import oracledb

# FastAPI 앱 생성
app = FastAPI()

# DB 설정
db_config = {
    "user": "rwg",
    "password": "1234",
    "dsn": "localhost:1521/XEPDB1"  
}

# 입력 데이터 모델 정의
class User(BaseModel):
    fullName: str
    gender: str | None = None
    birthDate: str | None = None   # "YYYY-MM-DD"
    contact: str | None = None
    address: str | None = None
    isDischarged: str | None = None
    protectionType: str | None = None

@app.post("/register")
async def register(user: User):
    try:
        # DB 연결
        conn = oracledb.connect(**db_config)
        cursor = conn.cursor()

        # SQL 실행
        cursor.execute("""
            INSERT INTO members (username,id,pwd, gender, birth_date, contact, address, is_discharged, protection_type)
            VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD'), :4, :5, :6, :7)
        """, (
            user.fullName, user.gender, user.birthDate,
            user.contact, user.address, user.isDischarged, user.protectionType
        ))

        conn.commit()
        return {"message": "회원가입이 완료되었습니다.!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB 저장 실패: {str(e)}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
