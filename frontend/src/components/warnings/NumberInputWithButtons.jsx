import React, { useRef } from "react";

export default function NumberInputWithButtons({ value, onChange, min = 0, max = 100, step = 1, ...props }) {
 const intervalRef = useRef(null);

  const changeValue = (delta) => {
    const newValue = Math.max(min, Math.min(max, Number(value) + delta));
    onChange(newValue);
  };

  const handleMouseDown = (delta) => {
    changeValue(delta);
    intervalRef.current = setInterval(() => changeValue(delta), 100);
  };

  const handleMouseUp = () => {
    clearInterval(intervalRef.current);
  };
  
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem" }}>
      <button
        type="button"
        className="plusminus-btn"
        style={{ padding: "0.3rem 0.7rem" }}
        onMouseDown={() => handleMouseDown(-step)}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onTouchStart={() => handleMouseDown(-step)}
        onTouchEnd={handleMouseUp}
      >–</button>
      <input
        type="number"
        className="input-field"
        value={
          value !== ""
            ? (props.step === 1 ? Math.round(Number(value)) : Number(value).toFixed(1))
            : ""
        }
        min={min}
        max={max}
        step={step}
        onChange={e => onChange(Number(e.target.value))}
        {...props}
        style={{ width: 70, textAlign: "center" }}
      />
      <button
        type="button"
        className="plusminus-btn"
        style={{ padding: "0.3rem 0.7rem" }}
        onMouseDown={() => handleMouseDown(step)}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onTouchStart={() => handleMouseDown(step)}
        onTouchEnd={handleMouseUp}
      >+</button>    
      </div>
  );
}