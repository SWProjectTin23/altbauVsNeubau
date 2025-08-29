import React from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Warnings from "./pages/Warnings";
import "./App.css";
import { AppErrorBoundary } from "./components/AppErrorBoundary";
import ConfirmEmail from "./pages/ConfirmEmail";

function App() {
  return (
    <BrowserRouter>
      <div className="font-sans layout-wrapper">
        <header className="custom-header">
          <div className="header-container">
            <h1 className="header-title">Dashboard – Altbau vs Neubau</h1>
            <Link to="/">
              <img src="/logo512.png" alt="Logo" className="header-logo" style={{ cursor: "pointer" }} />
            </Link>
          </div>
        </header>

        <AppErrorBoundary>
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/warnings" element={<Warnings />} />
              <Route path="/confirm-email" element={<ConfirmEmail />} />
            </Routes>
          </main>
        </AppErrorBoundary>

        <footer className="footer">
          <div className="footer-container">
            <p className="footer-text">
              © {new Date().getFullYear()} Altbau vs Neubau. Alle Rechte vorbehalten.
            </p>
            <div style={{ marginTop: "0.5rem" }}>
              <a href="mailto:altbauvsneubau@hrschmllr.de" style={{ color: "#fff" }}>Kontakt</a>
            </div>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}

export default App;