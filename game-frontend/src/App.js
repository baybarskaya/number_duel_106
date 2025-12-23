import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';

// Sayfaları içe aktar
import Login from './pages/Login';
import Register from './pages/Register';
import Lobby from './pages/Lobby';
import GameBoard from './pages/GameBoard';
import Profile from './pages/Profile';

function App() {
  return (
    <Router>
      <div className="App" style={{minHeight: '100vh', backgroundColor: '#f5f5f5'}}>
        <Routes>
          {/* Ana sayfa - Login'e yönlendir */}
          <Route path="/" element={<Navigate to="/login" replace />} />
          
          {/* Auth sayfaları */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Oyun sayfaları */}
          <Route path="/lobby" element={<Lobby />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/game/:roomId" element={<GameBoard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;