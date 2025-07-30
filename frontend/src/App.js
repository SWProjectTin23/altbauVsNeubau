import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./Dashboard";
import Warnings from "./pages/Warnings";
import "./App.css";

function App() {
  return (
    <BrowserRouter>
          <div className="min-h-screen bg-[#F9F9FE] font-sans">

            <header className="custom-header">
              <div className="header-container">
                <h1 className="header-title">Dashboard – Altbau vs Neubau</h1>
              </div>
            </header>

            <main className="px-4 py-6 sm:px-6 lg:px-8">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/warnwerte" element={<Warnings />} />
              </Routes>
            </main>
          </div>
        </BrowserRouter>
  );
}

export default App;
