import React from 'react';
import BenfordDashboard from './app/components/BenfordDashboard';

function App() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-slate-900 text-white p-4 shadow-md">
        <h1 className="text-xl font-bold">AuditFlow Platform</h1>
      </header>
      <main className="flex-1 p-8">
        <BenfordDashboard />
      </main>
    </div>
  );
}

export default App;
