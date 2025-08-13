import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Warnings from "./pages/Warnings";
import "./App.css";
import bgImage from './assets/Aussenaufnahme_Marienstrasse_Hanns-Voith-Campus_Schloss_Fotograf_Oliver_Vogel_Startseite.jpg';
import { AppErrorBoundary } from "./components/AppErrorBoundary";

function App() {
  return (
    <BrowserRouter>
      <div className="main-bg font-sans" style={{ position: "relative", minHeight: "100vh", overflow: "hidden" }}>
      <div
          className="bg-blur"
          style={{
            backgroundImage: `url(${bgImage})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            backgroundRepeat: 'no-repeat',
            filter: 'blur(10px)',
            position: 'absolute',
            inset: 0,
            width: '100%',
            height: '100%',
            zIndex: 0,
            pointerEvents: 'none',
          }}
        />
        <div style={{ position: "relative", zIndex: 1 }}>
        <header className="custom-header">
          <div className="header-container">
            <h1 className="header-title">Dashboard – Altbau vs Neubau</h1>
            <img src="/logo512.png" alt="Logo" className="header-logo" />
          </div>
        </header>

        <AppErrorBoundary>
          <main className="px-4 py-6 sm:px-6 lg:px-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/warnwerte" element={<Warnings />} />
            </Routes>
          </main>
        </AppErrorBoundary>

      <footer className="footer">
        <div className="footer-container">
          <p className="footer-text">
           © {new Date().getFullYear()} Altbau vs Neubau. Alle Rechte vorbehalten.
          </p>
          <div className="footer-links" style={{ marginTop: "0.5rem" }}>
            <a href="/impressum" style={{ color: "#fff", marginRight: "1rem" }}>Impressum</a>
            <a href="/datenschutz" style={{ color: "#fff" }}>Datenschutz</a>
          </div>
          <div style={{ marginTop: "0.5rem" }}>
            <a href="mailto:info@altbauvsneubau.de" style={{ color: "#fff" }}>Kontakt</a>
          </div>
        </div>
      </footer>
      </div>
    </div>
    </BrowserRouter>
  );
}

export default App;