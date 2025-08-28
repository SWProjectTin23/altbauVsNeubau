import React from "react";

export default function NumberInputWithButtons({ value, onChange, min = 0, max = 100, step = 1, ...props }) {
  const handleDecrease = () => {
    const newValue = Math.max(min, Number(value) - step);
    onChange(newValue);
  };
  const handleIncrease = () => {
    const newValue = Math.min(max, Number(value) + step);
    onChange(newValue);
  };
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem" }}>
      <button type="button" className="plusminus-btn" style={{ padding: "0.3rem 0.7rem" }} onClick={handleDecrease}>–</button>
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
      <button type="button" className="plusminus-btn" style={{ padding: "0.3rem 0.7rem" }} onClick={handleIncrease}>+</button>
    </div>
  );
}