import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./login.css";

const LockIcon = () => (
  <svg
    width="150"
    height="150"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    style={{ color: "#866ff2" }}
  >
    <path
      d="M17 11H7C5.89543 11 5 11.8954 5 13V19C5 20.1046 5.89543 21 7 21H17C18.1046 21 19 20.1046 19 19V13C19 11.8954 18.1046 11 17 11Z"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M8 11V7C8 5.67392 8.52678 4.40215 9.46447 3.46447C10.4021 2.52678 11.6739 2 13 2C14.3261 2 15.5979 2.52678 16.5355 3.46447C17.4732 4.40215 18 5.67392 18 7V11"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
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
          <LockIcon />
          <p style={{ fontSize: "20px", color: "#aaa" }}>아무거나 채워넣어라</p>
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
            <h1 className="title">지정주제... 로그인 페이지 입니다!</h1>
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
