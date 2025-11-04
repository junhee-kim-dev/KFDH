import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./register.css";

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

const steps = [
  {
    field: "name",
    label: "이름",
    type: "text",
    placeholder: "이름을 입력하세요",
  },
  { field: "gender", label: "성별", type: "radio", options: ["남성", "여성"] },
  { field: "birthDate", label: "생년월일", type: "date" },
  {
    field: "user_id",
    label: "아이디",
    type: "text",
    placeholder: "아이디를 입력하세요",
  },
  {
    field: "password",
    label: "비밀번호",
    type: "password",
    placeholder: "비밀번호를 입력하세요",
  },
];

const RegisterPage = () => {
  const [formData, setFormData] = useState({});
  const [currentStep, setCurrentStep] = useState(0);
  const [editingIndex, setEditingIndex] = useState(null);
  const navigate = useNavigate();

  // 입력 후 다음 단계 이동
  const handleNext = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (editingIndex === null) {
      setCurrentStep((prev) => Math.min(prev + 1, steps.length));
    }
    setEditingIndex(null);
  };

  const handleEdit = (stepIndex) => setEditingIndex(stepIndex);

  // 🔹 회원가입 요청 (FastAPI용)
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch("http://localhost:8000/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await res.json();

      if (res.ok) {
        alert(data.message || "회원가입 성공!");
        navigate("/login");
      } else {
        alert(data.detail || data.message || "회원가입 실패");
      }
    } catch (err) {
      alert("서버 오류: " + err.message);
    }
  };

  // 입력 필드 렌더링
  const renderField = (step, index) => {
    const value = formData[step.field] || "";
    const setValue = (v) =>
      setFormData((prev) => ({ ...prev, [step.field]: v }));

    switch (step.type) {
      case "text":
      case "password":
      case "date":
        return (
          <>
            <label className="label">{step.label}</label>
            <div className="inputGroup">
              <input
                type={step.type}
                className="input"
                placeholder={step.placeholder || ""}
                value={value}
                onChange={(e) => {
                  setValue(e.target.value);
                  if (step.type === "date" && e.target.value)
                    handleNext(step.field, e.target.value);
                }}
                onBlur={(e) => {
                  if (step.type !== "date") {
                    const v = e.target.value.trim();
                    if (v !== "") handleNext(step.field, v);
                  }
                }}
                onKeyDown={(e) => {
                  if (step.type !== "date" && e.key === "Enter") {
                    const v = e.target.value.trim();
                    if (v !== "") handleNext(step.field, v);
                  }
                }}
                autoFocus={editingIndex === index}
              />
            </div>
          </>
        );
      case "radio":
        return (
          <>
            <label className="label">{step.label}</label>
            <div className="radioGroup">
              {step.options.map((opt) => (
                <label key={opt} className="radioLabel">
                  <input
                    type="radio"
                    name={step.field}
                    value={opt}
                    checked={value === opt}
                    className="radioInput"
                    onChange={(e) => handleNext(step.field, e.target.value)}
                  />
                  {opt}
                </label>
              ))}
            </div>
          </>
        );
      default:
        return null;
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
        <div className="registerContainer">
          <div className="header">
            <span>로그인 하러가기 </span>
            <Link to="/login" className="signInLink">
              로그인
            </Link>
          </div>

          <div className="welcomeHeader">
            <h1 className="title">회원가입</h1>
            <p className="subtitle">한 항목씩 입력해주세요</p>
          </div>

          <form className="form" onSubmit={handleSubmit}>
            {steps.map((step, index) =>
              index < currentStep ? (
                <div key={step.field}>
                  {editingIndex === index ? (
                    <div className="activeField">
                      {renderField(step, index)}
                    </div>
                  ) : (
                    <div
                      className="summaryCard"
                      onClick={() => handleEdit(index)}
                    >
                      <strong>{step.label}:</strong> {formData[step.field]}
                    </div>
                  )}
                </div>
              ) : null
            )}

            {editingIndex === null && currentStep < steps.length && (
              <div className="activeField">
                {renderField(steps[currentStep], currentStep)}
              </div>
            )}

            {currentStep === steps.length && editingIndex === null && (
              <button type="submit" className="registerButton">
                가입하기
              </button>
            )}
          </form>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
