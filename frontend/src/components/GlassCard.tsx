import React from "react";

const GlassCard = ({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) => (
  <div
    className={`backdrop-blur-lg bg-white/5 border border-white/10 rounded-2xl shadow-xl p-6 ${className}`}
    style={{
      boxShadow: "0 8px 32px 0 rgba(31, 38, 135, 0.15)",
      transition: "box-shadow 0.3s cubic-bezier(.4,0,.2,1)",
    }}
  >
    {children}
  </div>
);

export default GlassCard;
