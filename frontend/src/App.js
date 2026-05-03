import React from 'react';
import Dashboard from './pages/Dashboard';
import ConflictReview from './pages/ConflictReview';
import AuditLog from './pages/AuditLog';

function App() {
    const [view, setView] = React.useState('dashboard');

    return (
        <div>
            <nav style={{ padding: '1rem', background: '#333', color: '#fff' }}>
                <button onClick={() => setView('dashboard')} style={navBtnStyle}>Dashboard</button>
                <button onClick={() => setView('conflicts')} style={navBtnStyle}>Conflicts</button>
                <button onClick={() => setView('audit')} style={navBtnStyle}>Audit Log</button>
            </nav>
            <main>
                {view === 'dashboard' && <Dashboard />}
                {view === 'conflicts' && <ConflictReview />}
                {view === 'audit' && <AuditLog />}
            </main>
        </div>
    );
}

const navBtnStyle = {
    background: 'none',
    border: 'none',
    color: 'white',
    marginRight: '1rem',
    cursor: 'pointer',
    fontSize: '1rem'
};

export default App;
