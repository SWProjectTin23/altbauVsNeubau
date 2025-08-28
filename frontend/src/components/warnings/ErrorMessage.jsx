import React from 'react';

export default function ErrorMessage({ message }) {
  if (!message) return null;
  return (
    <div className="error-message">
      <span style={{ fontSize: "1.5em", marginRight: "0.5em" }}>⚠️</span>
      {message}
    </div>
  );
}