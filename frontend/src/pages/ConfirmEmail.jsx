import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../utils/api";
import '../App.css';

export default function ConfirmEmail() {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState("pending");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const token = searchParams.get("token");
    if (!token) {
      setStatus("error");
      setMessage("Kein Bestätigungs-Token gefunden.");
      return;
    }

    async function confirm() {
      try {
        const res = await api.post("/confirm_email", { token });
        if (res.status === "success") {
          setStatus("success");
          setMessage("Deine E-Mail-Adresse wurde erfolgreich bestätigt. Du erhältst nun Alerts.");
        } else {
          setStatus("error");
          setMessage(res.message || "Bestätigung fehlgeschlagen.");
        }
      } catch (err) {
        setStatus("error");
        setMessage("Bestätigung fehlgeschlagen. Bitte versuche es später erneut.");
      }
    }
    confirm();
  }, [searchParams]);

  return (
    <div className="white-bg" style={{ maxWidth: 500, margin: "4rem auto", padding: "2rem", textAlign: "center" }}>
      <h2 className="section-title">E-Mail bestätigen</h2>
      {status === "pending" && <p>Bestätige deine E-Mail-Adresse...</p>}
      {status === "success" && <p style={{ color: "green", fontWeight: 600 }}>{message}</p>}
      {status === "error" && <p style={{ color: "red", fontWeight: 600 }}>{message}</p>}
    <button className="btn" onClick={() => window.location.href = "/"}>Zurück zur Startseite</button>
    </div>
  );
}