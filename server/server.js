import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import { pool } from "./db.js";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

// ======================
// JWT 인증 미들웨어
// ======================
const authMiddleware = (req, res, next) => {
  const token = req.headers.authorization?.split(" ")[1];
  if (!token) return res.status(401).json({ message: "토큰이 없습니다." });

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(403).json({ message: "유효하지 않은 토큰입니다." });
  }
};

// ======================
// 기본 라우트
// ======================
app.get("/", (req, res) => {
  res.send("✅ Server is running!");
});

app.get("/api/testdb", async (req, res) => {
  try {
    const result = await pool.query("SELECT NOW()");
    res.json({ server_time: result.rows[0] });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "DB 연결 실패" });
  }
});

// ======================
// 회원가입 라우트
// ======================
app.post("/api/auth/register", async (req, res) => {
  try {
    const { name, gender, birthDate, user_id, password } = req.body;

    if (!name || !gender || !birthDate || !user_id || !password) {
      return res.status(400).json({ message: "모든 필드를 입력해주세요." });
    }

    // 🔹 나이 계산
    const birthYear = new Date(birthDate).getFullYear();
    const currentYear = new Date().getFullYear();
    const age = currentYear - birthYear;

    // 🔹 비밀번호 암호화
    const hashedPassword = await bcrypt.hash(password, 10);

    const result = await pool.query(
      "INSERT INTO users (name, gender, age, user_id, password) VALUES ($1, $2, $3, $4, $5) RETURNING id, name, gender, age, user_id",
      [name, gender, age, user_id, hashedPassword]
    );

    res.status(201).json({ message: "회원가입 성공!", user: result.rows[0] });
  } catch (err) {
    console.error(err);
    if (err.code === "23505") {
      return res.status(400).json({ message: "이미 사용 중인 아이디입니다." });
    }
    res.status(500).json({ message: "회원가입 실패", error: err.message });
  }
});

// ======================
// 로그인 라우트
// ======================
app.post("/api/auth/login", async (req, res) => {
  try {
    const { user_id, password } = req.body;
    if (!user_id || !password)
      return res.status(400).json({ message: "모든 필드를 입력해주세요." });

    const userResult = await pool.query(
      "SELECT * FROM users WHERE user_id = $1",
      [user_id]
    );

    if (userResult.rows.length === 0)
      return res.status(400).json({ message: "존재하지 않는 아이디입니다." });

    const user = userResult.rows[0];

    // 🔹 비밀번호 비교
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch)
      return res.status(400).json({ message: "비밀번호가 일치하지 않습니다." });

    // 🔹 JWT 발급
    const token = jwt.sign(
      { id: user.id, user_id: user.user_id, name: user.name },
      process.env.JWT_SECRET,
      { expiresIn: "2h" } // 2시간 유지
    );

    res.json({
      message: "로그인 성공!",
      token,
      user: {
        id: user.id,
        name: user.name,
        gender: user.gender,
        age: user.age,
      },
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "로그인 실패", error: err.message });
  }
});

// ======================
// 로그인 상태 검증 라우트
// ======================
app.get("/api/auth/me", authMiddleware, async (req, res) => {
  try {
    const userResult = await pool.query(
      "SELECT id, name, gender, age, user_id FROM users WHERE id = $1",
      [req.user.id]
    );

    if (userResult.rows.length === 0)
      return res.status(404).json({ message: "사용자를 찾을 수 없습니다." });

    res.json({ user: userResult.rows[0] });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "사용자 정보 조회 실패" });
  }
});

// ======================
// 서버 실행
// ======================
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`🚀 Server running on port ${PORT}`));
