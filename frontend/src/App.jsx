import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Login from './Login';
import Dashboard from './Dashboard';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/dashboard" element={<Dashboard />} />
    </Routes>
  );
}