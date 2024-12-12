import React from 'react';
import ReactDOM from 'react-dom/client'; // Usar ReactDOM.createRoot no React 18
import { BrowserRouter } from 'react-router-dom'; // Para roteamento
import './index.css'; // Estilos globais
import App from './App'; // Componente principal
import reportWebVitals from './reportWebVitals'; // Métricas (opcional)

// Usar ReactDOM.createRoot para inicializar o App
const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <BrowserRouter> {/* Envolva o App com BrowserRouter */}
      <App />
    </BrowserRouter>
  </React.StrictMode>
);

// Para métricas de performance (opcional)
reportWebVitals();
