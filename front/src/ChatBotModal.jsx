import React, { useState } from "react";
import styles from "./chatbot.module.css";

const ChatBotModal = ({ onClose }) => {
  const [messages, setMessages] = useState([
    {
      from: "bot",
      text: "안녕하세요! 스타일 추천 AI 어시스턴트입니다. 어떤 스타일을 찾고 계신가요? 😊",
    },
  ]);
  const [input, setInput] = useState("");

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg = { from: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    try {
      const res = await fetch("http://localhost:8000/api/fashionchat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input, city: "Seoul" }),
      });
      const data = await res.json();

      const botMsg = {
        from: "bot",
        text: `${data.weather}\n\n${data.response}`,
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { from: "bot", text: "❌ 서버와 통신 중 오류가 발생했습니다." },
      ]);
    }
  };

  const quickReplies = [
    "캐주얼 스타일",
    "포멀 스타일",
    "색상 추천",
    "예산 상담",
  ];

  return (
    <div className={styles.chatbotModal}>
      {/* 🔹 헤더 */}
      <div className={styles.chatbotHeader}>
        <div className={styles.chatbotTitle}>✨ 스타일 AI 어시스턴트</div>
        <button className={styles.chatbotClose} onClick={onClose}>
          ✕
        </button>
      </div>

      {/* 🔹 메시지 영역 */}
      <div className={styles.chatbotBody}>
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`${styles.chatMsg} ${
              msg.from === "bot" ? styles.bot : styles.user
            }`}
          >
            <div className={styles.msgBubble}>{msg.text}</div>
          </div>
        ))}
      </div>

      {/* 🔹 빠른 답변 */}
      <div className={styles.quickReplies}>
        {quickReplies.map((q, i) => (
          <button key={i} onClick={() => setInput(q)}>
            {q}
          </button>
        ))}
      </div>

      {/* 🔹 입력창 */}
      <div className={styles.chatbotInput}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="메시지를 입력하세요..."
        />
        <button onClick={handleSend}>➤</button>
      </div>
    </div>
  );
};

export default ChatBotModal;
