import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./fitting.module.css";

const FittingPage = () => {
  const navigate = useNavigate();
  const [userImage, setUserImage] = useState(null);
  const [recommended, setRecommended] = useState([]);
  const [selectedCloth, setSelectedCloth] = useState(null);
  const [user, setUser] = useState(null);
  const [resultUrl, setResultUrl] = useState("");
  const [loading, setLoading] = useState(false);

  // ✅ localStorage에서 추천 결과 불러오기
  useEffect(() => {
    const stored = localStorage.getItem("recommended_items");
    if (stored) setRecommended(JSON.parse(stored));
  }, []);

  // ✅ 로그인된 사용자 정보 불러오기
  useEffect(() => {
    fetch("http://localhost:8000/api/auth/me", { credentials: "include" })
      .then((res) => res.json())
      .then((data) => {
        if (data.user) setUser(data.user);
      })
      .catch(() => console.log("사용자 정보를 불러오지 못했습니다."));
  }, []);

  // ✅ 내 사진 업로드
  const handleUserChange = (e) => {
    const file = e.target.files[0];
    if (file) setUserImage(file);
  };

  // ✅ 로그아웃
  const handleLogout = async () => {
    try {
      await fetch("http://localhost:8000/api/auth/logout", {
        method: "POST",
        credentials: "include",
      });
      alert("로그아웃 되었습니다.");
      navigate("/login");
    } catch (err) {
      console.error("로그아웃 실패:", err);
    }
  };

  // ✅ 가상 피팅 실행
  const handleTryOn = async () => {
    if (!userImage || !selectedCloth) {
      alert("전신 사진과 의상을 모두 선택해주세요!");
      return;
    }

    const formData = new FormData();
    formData.append("vton_img", userImage);
    formData.append("garm_img_path", selectedCloth.img_path);
    formData.append("category", "Upper-body");

    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/fitting", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setResultUrl(data.result_url);
    } catch (err) {
      console.error("가상피팅 실패:", err);
    }
    setLoading(false);
  };

  return (
    <div className={styles["fitting-container"]}>
      <nav className={styles.navbar}>
        <div className={styles["nav-left"]}>
          <ul className={styles["nav-links"]}>
            <li onClick={() => navigate("/")}>K-Fashion</li>
            <li onClick={() => navigate("/mainpage")}>홈</li>
            <li className={styles.active} onClick={() => navigate("/fitting")}>
              가상피팅
            </li>
            <li onClick={() => navigate("/recommend")}>추천</li>
          </ul>
        </div>

        <div className={styles["nav-right"]}>
          {user && <span className={styles["user-name"]}>{user.name}님</span>}
          <button className={styles.logoutBtn} onClick={handleLogout}>
            로그아웃
          </button>
        </div>
      </nav>

      <div className={styles["page-header"]}>
        <span className={styles.aiBadge}>🪞 AI 가상 피팅</span>
        <h2>가상으로 의상 입어보기</h2>
        <p>추천받은 의상을 선택해 본인 사진에 입혀보세요</p>
      </div>

      <div className={styles["fitting-content"]}>
        <div className={styles["left-panel"]}>
          <h3>📸 내 사진 업로드</h3>
          <p>전신 사진을 업로드해주세요</p>

          <label className={styles["upload-box"]} htmlFor="upload-user">
            {userImage ? (
              <img
                src={URL.createObjectURL(userImage)}
                alt="preview"
                className={styles["upload-preview"]}
              />
            ) : (
              <div className={styles["upload-placeholder"]}>
                <span className={styles["upload-icon"]}>⬆️</span>
                <p>이미지를 클릭하거나 드래그하여 업로드</p>
              </div>
            )}
          </label>
          <input
            id="upload-user"
            type="file"
            accept="image/*"
            style={{ display: "none" }}
            onChange={handleUserChange}
          />
        </div>

        <div className={styles["right-panel"]}>
          <h3>👕 추천받은 의상</h3>
          <p>AI가 추천한 의상 중 하나를 선택해주세요</p>

          {recommended.length === 0 ? (
            <p>추천받은 의상이 없습니다. 먼저 추천 탭에서 받아보세요!</p>
          ) : (
            <div className={styles["cloth-list"]}>
              {recommended.map((item, i) => (
                <div
                  key={i}
                  className={`${styles["cloth-card"]} ${
                    selectedCloth?.id === item.id ? styles.selected : ""
                  }`}
                  onClick={() => setSelectedCloth(item)}
                >
                  <img
                    src={`http://localhost:8000/static/images/${item.img_path
                      .split("/")
                      .pop()}`}
                    alt={item.name}
                  />
                  <div className={styles.info}>
                    <h4>{item.brand}</h4>
                    <p>{item.name}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className={styles["bottom-section"]}>
        <button className={styles["tryon-btn"]} onClick={handleTryOn}>
          AI 가상 피팅 실행
        </button>

        {loading && <p>AI가 이미지를 합성 중입니다...</p>}

        {resultUrl && (
          <div className={styles["result-section"]}>
            <h3>결과 미리보기</h3>
            <img
              src={resultUrl}
              alt="result"
              className={styles["result-img"]}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default FittingPage;
