import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LoginPage from "./login";
import RegisterPage from "./regist";
import ProtectedRoute from "./ProtectedRoute";
import MainPage from "./mainpage";

const Home = ({ user, handleLogout }) => (
  <div style={{ textAlign: "center", marginTop: "100px" }}>
    <h2>환영합니다, {user?.name}님 👋</h2>
    <button onClick={handleLogout}>로그아웃</button>
  </div>
);

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // ✅ 앱이 처음 로드될 때 로그인 상태 확인
  useEffect(() => {
    const checkLogin = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/auth/me", {
          method: "GET",
          credentials: "include", // 쿠키 자동 전송
        });

        if (!res.ok) {
          setUser(null);
        } else {
          const data = await res.json();
          setUser(data.user);
        }
      } catch (err) {
        console.error("인증 확인 실패:", err);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    checkLogin();
  }, []);

  // ✅ 로그아웃 (서버 쿠키 삭제)
  const handleLogout = async () => {
    try {
      await fetch("http://localhost:8000/api/auth/logout", {
        method: "POST",
        credentials: "include",
      });
      setUser(null);
    } catch (err) {
      console.error("로그아웃 실패:", err);
    }
  };

  if (loading)
    return <div style={{ textAlign: "center", marginTop: "100px" }}></div>;

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage setUser={setUser} />} />
        <Route path="/regist" element={<RegisterPage />} />
        <Route path="/mainpage" element={<MainPage user={user} />} />
        <Route
          path="/"
          element={
            <ProtectedRoute user={user}>
              <Home user={user} handleLogout={handleLogout} />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
