import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./login.css";

const KFashionLogo = () => (
  <svg
    width="150"
    height="150"
    viewBox="0 0 200 200"
    xmlns="http://www.w3.org/2000/svg"
  >
    <rect width="200" height="200" rx="20" fill="transparent" />
    <defs>
      <linearGradient id="grad" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stopColor="#a67cff" />
        <stop offset="100%" stopColor="#c77bff" />
      </linearGradient>
    </defs>

    {/* K 스티치 라인 */}
    <path
      d="
        M55 30 
        L55 170 
        M55 100 
        L145 30 
        M55 100 
        L145 170
      "
      stroke="url(#grad)"
      strokeWidth="10"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeDasharray="18 12"
      fill="none"
    />

    {/* 텍스트 */}
    <text
      x="50%"
      y="190"
      textAnchor="middle"
      fill="#444"
      fontFamily="Inter, Pretendard, sans-serif"
      fontSize="26"
      fontWeight="600"
    >
      K-Fashion
    </text>
  </svg>
);

const EyeIcon = () => (
  <svg
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
    <circle cx="12" cy="12" r="3"></circle>
  </svg>
);

const LoginPage = ({ setUser }) => {
  const navigate = useNavigate();
  const [user_id, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  // 🔹 로그인 요청 (FastAPI 버전)
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include", // ← 반드시 추가 (쿠키 수신/전송 허용)
        body: JSON.stringify({ user_id, password }),
      });

      const data = await res.json();

      if (res.ok) {
        // 🔸 전역 상태 업데이트
        setUser(data.user);
        alert("로그인 성공!");
        navigate("/mainpage");
      } else {
        alert(
          data.detail ||
            data.message ||
            "로그인 실패. 아이디와 비밀번호를 확인하세요."
        );
      }
    } catch (err) {
      alert("서버 오류: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="leftPanel">
        <div>
          <KFashionLogo />
        </div>
      </div>

      <div className="rightPanel">
        <div className="logo"></div>
        <div className="loginContainer">
          <div className="header">
            <span>계정이 없으신가요?</span>
            <Link to="/regist" className="signInLink">
              회원가입
            </Link>
          </div>

          <div className="welcomeHeader">
            <h1 className="title">K-Fashion 로그인 페이지 입니다!</h1>
            <p className="subtitle">로그인하세요</p>
          </div>

          <form className="form" onSubmit={handleLogin}>
            <label htmlFor="user_id" className="label">
              아이디
            </label>
            <div className="inputGroup">
              <input
                type="text"
                id="user_id"
                placeholder="아이디를 입력하세요"
                className="input"
                value={user_id}
                onChange={(e) => setUserId(e.target.value)}
                required
              />
            </div>

            <label htmlFor="password" className="label">
              비밀번호
            </label>
            <div className="inputGroup">
              <input
                type="password"
                id="password"
                placeholder="비밀번호를 입력하세요"
                className="input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <span className="passwordIcon">
                <EyeIcon />
              </span>
            </div>

            <button type="submit" className="loginButton" disabled={loading}>
              {loading ? "로그인 중..." : "로그인"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
