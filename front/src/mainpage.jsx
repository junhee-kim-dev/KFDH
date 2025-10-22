// import React from "react";
// import { useNavigate } from "react-router-dom";
// import "./mainpage.css"; // 스타일 분리

// const MainPage = ({ user }) => {
//   const navigate = useNavigate();

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

//   return (
//     <div className="mainpage">
//       {/* 상단 네비게이션 */}
//       <nav className="navbar">
//         <div className="nav-left">
//           <ul className="nav-links">
//             <li>K-Fashion</li>
//             <li>홈</li>
//             <li>가상 피팅</li>
//             <li>트렌드</li>
//             <li>추천</li>
//             <li>소셜</li>
//           </ul>
//         </div>

//         <div className="nav-right">
//           <input
//             type="text"
//             placeholder="스타일, 의상, 브랜드 검색..."
//             className="search-bar"
//           />
//           <button className="logout-btn" onClick={handleLogout}>
//             로그아웃
//           </button>
//         </div>
//       </nav>

//       {/* Hero Section */}
//       <section className="hero">
//         <div className="hero-text">
//           <p className="ai-badge">✨ AI 기반 스타일 추천</p>
//           <h1>
//             당신만의 완벽한 <br />
//             <span className="highlight">스타일을 찾아보세요</span>
//           </h1>
//           <p className="subtext">
//             AI가 분석한 의상을 추천받으세요.
//             <br /> 매일 업데이트되는 트렌디한 스타일을 만나보세요.
//           </p>
//           <div className="hero-buttons">
//             <button className="primary-btn">검색 & 추천</button>
//             <button className="secondary-btn">인기 스타일 보기</button>
//           </div>
//           <div className="stats">
//             <div>
//               <strong>10만+</strong> 활성 사용자
//             </div>
//             <div>
//               <strong>5천+</strong> 큐레이션 룩
//             </div>
//             <div>
//               <strong>98%</strong> 만족도
//             </div>
//           </div>
//         </div>
//         <div className="hero-image">
//           <img src="images/c1.png" alt="AI 스타일 추천" />
//         </div>
//       </section>

//       {/* 스타일 카테고리 섹션 */}
//       <section className="categories">
//         <h2>인기 스타일 카테고리</h2>
//         <p>다양한 시즌과 상황에 맞는 스타일을 탐색해보세요</p>
//         <div className="category-grid">
//           {[
//             {
//               title: "캐주얼",
//               desc: "편안한 일상 스타일",
//               img: "images/c1.png",
//             },
//             {
//               title: "비즈니스",
//               desc: "프로페셔널한 룩",
//               img: "images/c1.png",
//             },
//             {
//               title: "썸머",
//               desc: "시원한 여름 스타일",
//               img: "images/c1.png",
//             },
//             {
//               title: "윈터",
//               desc: "따뜻한 겨울 패션",
//               img: "images/c1.png",
//             },
//           ].map((cat, i) => (
//             <div key={i} className="category-card">
//               <img src={cat.img} alt={cat.title} />
//               <div className="overlay">
//                 <h3>{cat.title}</h3>
//                 <p>{cat.desc}</p>
//               </div>
//             </div>
//           ))}
//         </div>
//       </section>

//       {/* 트렌딩 섹션 */}
//       <section className="trending">
//         <h2>트렌딩 의상</h2>
//         <p>지금 가장 인기 있는 스타일을 만나보세요</p>
//         <div className="trend-grid">
//           {[
//             {
//               title: "모던 시크",
//               tag: "트렌디",
//               likes: 2453,
//               img: "images/c1.png",
//             },
//             {
//               title: "스트릿 캐주얼",
//               tag: "인기",
//               likes: 1892,
//               img: "images/c1.png",
//             },
//             {
//               title: "오피스 룩",
//               tag: "추천",
//               likes: 1654,
//               img: "images/c1.png",
//             },
//             {
//               title: "썸머 컬렉션",
//               tag: "NEW",
//               likes: 2211,
//               img: "images/c1.png",
//             },
//           ].map((item, i) => (
//             <div key={i} className="trend-card">
//               <img src={item.img} alt={item.title} />
//               <div className="tag">{item.tag}</div>
//               <div className="info">
//                 <h4>{item.title}</h4>
//                 <p>❤️ {item.likes.toLocaleString()}</p>
//               </div>
//             </div>
//           ))}
//         </div>
//       </section>

//       {/* 푸터 */}
//       <footer>
//         <p>© 2025 StyleMatch. All Rights Reserved.</p>
//       </footer>
//     </div>
//   );
// };

// export default MainPage;

import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./mainpage.css";

const MainPage = ({ user }) => {
  const navigate = useNavigate();
  const [products, setProducts] = useState([]); // DB에서 가져온 상품 저장

  // 1️⃣ DB에서 상품 데이터 불러오기
  useEffect(() => {
    fetch("http://localhost:8000/api/products")
      .then((res) => res.json())
      .then((data) => {
        console.log("📦 불러온 상품 데이터:", data.products);
        setProducts(data.products);
      })
      .catch((err) => console.error("데이터 불러오기 실패:", err));
  }, []);

  // 2️⃣ 로그아웃 핸들러
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

  return (
    <div className="mainpage">
      {/* 상단 네비게이션 */}
      <nav className="navbar">
        <div className="nav-left">
          <ul className="nav-links">
            <li>K-Fashion</li>
            <li>홈</li>
            <li>가상 피팅</li>
            <li>트렌드</li>
            <li>추천</li>
            <li>소셜</li>
          </ul>
        </div>

        <div className="nav-right">
          <input
            type="text"
            placeholder="스타일, 의상, 브랜드 검색..."
            className="search-bar"
          />
          <button className="logout-btn" onClick={handleLogout}>
            로그아웃
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-text">
          <p className="ai-badge">✨ AI 기반 스타일 추천</p>
          <h1>
            당신만의 완벽한 <br />
            <span className="highlight">스타일을 찾아보세요</span>
          </h1>
          <p className="subtext">
            AI가 분석한 의상을 추천받으세요.
            <br /> 매일 업데이트되는 트렌디한 스타일을 만나보세요.
          </p>
          <div className="hero-buttons">
            <button className="primary-btn">검색 & 추천</button>
            <button className="secondary-btn">인기 스타일 보기</button>
          </div>
        </div>
        <div className="hero-image">
          <img src="images/c1.png" alt="AI 스타일 추천" />
        </div>
      </section>

      {/* 트렌딩 섹션 (DB 연결됨) */}
      <section className="trending">
        <h2>트렌딩 의상</h2>
        <p>지금 가장 인기 있는 스타일을 만나보세요</p>

        <div className="trend-grid">
          {products.length === 0 ? (
            <p>⏳ 데이터를 불러오는 중...</p>
          ) : (
            products.map((item, i) => (
              <div key={i} className="trend-card">
                <img
                  src={`http://localhost:8000/static/${item.img_path
                    .split("/")
                    .pop()}`}
                  alt={item.name}
                />

                <div className="tag">{item.brand}</div>
                <div className="info">
                  <h4>{item.name}</h4>

                  <p className="price">{item.price.toLocaleString()}원</p>
                  <p>❤️ {item.likes.toLocaleString()}</p>
                </div>
              </div>
            ))
          )}
        </div>
      </section>

      {/* 푸터 */}
      <footer>
        <p>© 2025 StyleMatch. All Rights Reserved.</p>
      </footer>
    </div>
  );
};

export default MainPage;
