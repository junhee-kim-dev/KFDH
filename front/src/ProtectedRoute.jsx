import React from "react";
import { Navigate } from "react-router-dom";

const ProtectedRoute = ({ user, children }) => {
  if (!user) {
    alert("로그인이 필요합니다.");
    return <Navigate to="/login" replace />;
  }
  return children;
};

export default ProtectedRoute;
