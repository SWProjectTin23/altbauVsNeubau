import React from 'react';

export default function ErrorMessage({ message }) {
  if (!message) return null;
  return (
    <div className="error-message" style={{ color: "#e2001a", marginTop: 16 }}>
      {message}
    </div>
  );
}
