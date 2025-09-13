import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import keycloak from './keycloak';

const root = ReactDOM.createRoot(document.getElementById('root'));


root.render(<div>Lade...</div>);

keycloak.init({ onLoad: 'login-required' })
  .then(authenticated => {
    if (authenticated) {
      root.render(
        <React.StrictMode>
          <App keycloak={keycloak} />
        </React.StrictMode>
      );
    } else {
      keycloak.login();
    }
  })
  .catch(err => {
    console.error("Keycloak init failed:", err);
    // Optional: Lade-Screen mit Fehler anzeigen
    root.render(<div>Fehler beim Laden der Authentifizierung</div>);
  });
