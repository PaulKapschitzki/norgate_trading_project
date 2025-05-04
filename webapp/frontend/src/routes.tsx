import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Screener from './pages/Screener';

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/screener" replace />} />
      <Route path="/screener" element={<Screener />} />
      {/* Weitere Routen für zukünftige Features */}
      <Route path="/backtests" element={<div>Backtests (Coming Soon)</div>} />
      <Route path="/performance" element={<div>Performance (Coming Soon)</div>} />
    </Routes>
  );
};

export default AppRoutes;