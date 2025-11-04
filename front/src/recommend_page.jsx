// import React, { useState, useEffect } from "react";
// import { useNavigate } from "react-router-dom";
// import "./recommend_page.css";

// const RecommendPage = () => {
//   const navigate = useNavigate();
//   const [imageFile, setImageFile] = useState(null);
//   const [preview, setPreview] = useState("");
//   const [textPrompt, setTextPrompt] = useState("");
//   const [results, setResults] = useState([]);
//   const [loading, setLoading] = useState(false);
//   const [user, setUser] = useState(null); // ✅ 로그인 사용자 정보

//   // ✅ 로그인된 사용자 정보 불러오기
//   useEffect(() => {
//     fetch("http://localhost:8000/api/auth/me", { credentials: "include" })
//       .then((res) => res.json())
//       .then((data) => {
//         if (data.user) setUser(data.user);
//       })
//       .catch(() => console.log("사용자 정보를 불러오지 못했습니다."));
//   }, []);

//   const handleImageChange = (e) => {
//     const file = e.target.files[0];
//     if (file) {
//       setImageFile(file);
//       setPreview(URL.createObjectURL(file));
//     }
//   };

//   // ✅ 로그아웃
//   const handleLogout = async () => {
//     try {
//       await fetch("http://localhost:8000/api/auth/logout", {
//         method: "POST",
//         credentials: "include",
//       });
//       alert("로그아웃 되었습니다.");
//       navigate("/login");
//     } catch (err) {
//       console.error("로그아웃 실패:", err);
//     }
//   };

//   const handleRecommend = async () => {
//     if (!imageFile && !textPrompt) {
//       alert("이미지 또는 설명을 입력하세요!");
//       return;
//     }

//     const formData = new FormData();
//     if (imageFile) formData.append("file", imageFile);
//     formData.append("text_prompt", textPrompt);

//     setLoading(true);
//     try {
//       const res = await fetch("http://localhost:8000/api/recommend_hybrid", {
//         method: "POST",
//         body: formData,
//       });
//       const data = await res.json();
//       setResults(data.recommendations || []);
//       localStorage.setItem(
//         "recommended_items",
//         JSON.stringify(data.recommendations)
//       );
//     } catch (err) {
//       console.error("추천 실패:", err);
//     }
//     setLoading(false);
//   };

//   return (
//     <div className="mainpage">
//       {/* ✅ 네비게이션바 */}
//       <nav className="navbar">
//         <div className="nav-left">
//           <ul className="nav-links">
//             <li onClick={() => navigate("/")}>K-Fashion</li>
//             <li onClick={() => navigate("/mainpage")}>홈</li>
//             <li onClick={() => navigate("/fitting")}>가상 피팅</li>
//             <li className="active" onClick={() => navigate("/recommend")}>
//               추천
//             </li>
//           </ul>
//         </div>

//         <div className="nav-right">
//           {/* ✅ 로그인 사용자 이름 표시 */}
//           {user && <span className="user-name"> {user.name}님</span>}
//           <button className="logout-btn" onClick={handleLogout}>
//             로그아웃
//           </button>
//         </div>
//       </nav>

//       {/* ✅ 전체 컨테이너 */}
//       <div className="recommend-container">
//         {/* 🔹 이미지 업로드 카드 */}
//         <div className="recommend-card">
//           <h3>이미지 업로드</h3>
//           <p>참고하고 싶은 스타일의 이미지를 업로드해주세요 (선택사항)</p>

//           <label className="upload-box" htmlFor="image-upload">
//             {preview ? (
//               <img src={preview} alt="preview" className="upload-preview" />
//             ) : (
//               <div className="upload-placeholder">
//                 <span className="upload-icon">⬆️</span>
//                 <p>이미지를 드래그하거나 클릭하여 업로드</p>
//                 <small>JPG, PNG, GIF 형식 지원 (최대 10MB)</small>
//               </div>
//             )}
//           </label>
//           <input
//             id="image-upload"
//             type="file"
//             accept="image/*"
//             style={{ display: "none" }}
//             onChange={handleImageChange}
//           />
//         </div>

//         {/* 🔹 텍스트 입력 카드 */}
//         <div className="recommend-card">
//           <h3>스타일 설명</h3>
//           <p>원하는 스타일, 착용 상황, 선호 색상 등을 자유롭게 입력해주세요.</p>
//           <textarea
//             placeholder={`예시: 20대 중반 남성입니다. 편안하면서도 깔끔한 데일리룩을 찾고 있어요. 블랙, 화이트, 그레이 톤을 선호하고 미니멀한 스타일을 원합니다. 주로 카페나 사무실에서 착용할 예정이에요.`}
//             value={textPrompt}
//             onChange={(e) => setTextPrompt(e.target.value)}
//             rows={6}
//           ></textarea>
//         </div>

//         {/* 🔹 추천 버튼 */}
//         <button className="primary-btn big" onClick={handleRecommend}>
//           추천받기
//         </button>

//         {/* 🔹 결과 표시 */}
//         {loading && <p style={{ marginTop: "30px" }}>AI가 분석 중입니다...</p>}
//         {!loading && results.length > 0 && (
//           <div className="trend-grid" style={{ marginTop: "40px" }}>
//             {results.map((item, i) => (
//               <div key={i} className="trend-card">
//                 <img
//                   src={`http://localhost:8000/static/images/${item.img_path
//                     .split("/")
//                     .pop()}`}
//                   alt={item.name}
//                 />
//                 <div className="info">
//                   <h4>{item.brand}</h4>
//                   <p>{item.name}</p>
//                   <p>Score: {(item.hybrid_similarity * 100).toFixed(1)}%</p>
//                 </div>
//               </div>
//             ))}
//           </div>
//         )}
//       </div>
//     </div>
//   );
// };

// export default RecommendPage;

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./recommend_page.module.css";
import ChatBotButton from "./ChatBotButton";

const RecommendPage = () => {
  const navigate = useNavigate();
  const [imageFile, setImageFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [textPrompt, setTextPrompt] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/auth/me", { credentials: "include" })
      .then((res) => res.json())
      .then((data) => {
        if (data.user) setUser(data.user);
      })
      .catch(() => console.log("사용자 정보를 불러오지 못했습니다."));
  }, []);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
      setPreview(URL.createObjectURL(file));
    }
  };

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

  const handleRecommend = async () => {
    if (!imageFile && !textPrompt) {
      alert("이미지 또는 설명을 입력하세요!");
      return;
    }

    const formData = new FormData();
    if (imageFile) formData.append("file", imageFile);
    formData.append("text_prompt", textPrompt);

    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/recommend_hybrid", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setResults(data.recommendations || []);
      localStorage.setItem(
        "recommended_items",
        JSON.stringify(data.recommendations)
      );
    } catch (err) {
      console.error("추천 실패:", err);
    }
    setLoading(false);
  };

  return (
    <div className={styles.recommendWrapper}>
      {/* 🔹 네비게이션바 */}
      <nav className={styles.navbar}>
        <div className={styles.navLeft}>
          <ul className={styles.navLinks}>
            <li onClick={() => navigate("/")}>K-Fashion</li>
            <li onClick={() => navigate("/mainpage")}>홈</li>
            <li onClick={() => navigate("/fitting")}>가상 피팅</li>
            <li
              className={styles.active}
              onClick={() => navigate("/recommend")}
            >
              추천
            </li>
          </ul>
        </div>

        <div className={styles.navRight}>
          {user && <span className={styles.userName}>{user.name}님</span>}
          <button className={styles.logoutBtn} onClick={handleLogout}>
            로그아웃
          </button>
        </div>
      </nav>

      {/* 🔹 헤더 */}
      <div className={styles.header}>
        <p className={styles.headerSub}>👗 AI 기반 스마트 추천</p>
        <h1 className={styles.headerTitle}>나만의 스타일 찾기</h1>
        <p className={styles.headerDesc}>
          이미지를 업로드하고 선호하는 스타일을 설명해주세요
        </p>
      </div>

      {/* 🔹 메인 컨테이너 */}
      <div className={styles.recommendContainer}>
        <div className={styles.inputSection}>
          {/* 이미지 업로드 */}
          <div className={styles.inputCard}>
            <h3>이미지 업로드</h3>
            <p>참고하고 싶은 스타일의 이미지를 업로드해주세요 (선택사항)</p>

            <label className={styles.uploadBox} htmlFor="image-upload">
              {preview ? (
                <img
                  src={preview}
                  alt="preview"
                  className={styles.uploadPreview}
                />
              ) : (
                <div className={styles.uploadPlaceholder}>
                  <span className={styles.uploadIcon}>📤</span>
                  <p>이미지를 드래그하거나 클릭하여 업로드</p>
                  <small>JPG, PNG, GIF 형식 지원 (최대 10MB)</small>
                </div>
              )}
            </label>
            <input
              id="image-upload"
              type="file"
              accept="image/*"
              style={{ display: "none" }}
              onChange={handleImageChange}
            />
          </div>

          {/* 스타일 설명 */}
          <div className={styles.inputCard}>
            <h3>스타일 설명</h3>
            <p>
              원하는 스타일, 착용 상황, 선호 색상 등을 자유롭게 입력해주세요.
            </p>
            <textarea
              className={styles.textarea}
              placeholder={`예시: 20대 중반 남성입니다. 편안하면서도 깔끔한 데일리룩을 찾고 있어요. 블랙, 화이트, 그레이 톤을 선호하고 미니멀한 스타일을 원합니다.`}
              value={textPrompt}
              onChange={(e) => setTextPrompt(e.target.value)}
              rows={7}
            ></textarea>

            <div className={styles.keywordRow}>
              {["캐주얼", "포멀", "미니멀", "스트릿", "빈티지", "스포티"].map(
                (tag) => (
                  <button
                    key={tag}
                    onClick={() => setTextPrompt((t) => t + " " + tag)}
                  >
                    {tag}
                  </button>
                )
              )}
            </div>
          </div>
        </div>

        {/* 🔹 추천 버튼 */}
        <button className={styles.recommendBtn} onClick={handleRecommend}>
          {loading ? "AI가 분석 중..." : "맞춤 추천 받기"}
        </button>

        {/* 🔹 결과 */}
        {results.length > 0 && (
          <div className={styles.trendGrid}>
            {results.map((item, i) => (
              <div key={i} className={styles.trendCard}>
                <img
                  src={`http://localhost:8000/static/images/${item.img_path
                    .split("/")
                    .pop()}`}
                  alt={item.name}
                />
                <div className={styles.info}>
                  <h4>{item.brand}</h4>
                  <p>{item.name}</p>
                  <p className={styles.score}>
                    AI 추천률 {(item.hybrid_similarity * 100).toFixed(1)}%
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 🔹 챗봇 버튼 */}
      <ChatBotButton />

      {/* 🔹 하단 정보 */}
      <div className={styles.featureSection}>
        {[
          {
            icon: "🎯",
            title: "정확한 분석",
            text: "AI가 이미지와 설명을 함께 분석하여 스타일을 이해합니다.",
          },
          {
            icon: "💜",
            title: "맞춤형 추천",
            text: "사용자 취향에 맞춘 스타일 조합을 제안합니다.",
          },
          {
            icon: "✨",
            title: "쉬운 사용",
            text: "이미지 업로드와 간단한 설명만으로 추천을 받을 수 있습니다.",
          },
        ].map((f, i) => (
          <div key={i} className={styles.featureCard}>
            <span className={styles.icon}>{f.icon}</span>
            <h4>{f.title}</h4>
            <p>{f.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecommendPage;
