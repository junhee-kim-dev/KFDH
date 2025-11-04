import React, { useState } from "react";
import ChatBotModal from "./ChatBotModal";
import styles from "./chatbot.module.css";

const ChatBotButton = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* 🔹 플로팅 버튼 */}
      <div className={styles.chatbotFab} onClick={() => setIsOpen(!isOpen)}>
        💬
      </div>

      {/* 🔹 챗봇 모달 */}
      {isOpen && <ChatBotModal onClose={() => setIsOpen(false)} />}
    </>
  );
};

export default ChatBotButton;
