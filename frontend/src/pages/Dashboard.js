import React, { useState, useEffect } from 'react';

function Dashboard() {
    const [status, setStatus] = useState({});

    useEffect(() => {
        // In actual dev, this would point to the backend URL or use a proxy
        fetch('http://localhost:8000/api/v1/ingestion/status')
            .then(res => res.json())
            .then(data => setStatus(data))
            .catch(err => console.error("Error fetching status:", err));
    }, []);

    return (
        <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
            <h1 style={{ fontSize: '2rem', marginBottom: '1.5rem' }}>SanchaarSetu Dashboard</h1>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem' }}>
                <StatusCard title="Tier 1 (Webhooks)" status={status.tier1} color="#dcfce7" />
                <StatusCard title="Tier 2 (Polling)" status={status.tier2} color="#dbeafe" />
                <StatusCard title="Tier 3 (CDC)" status={status.tier3} color="#f3e8ff" />
            </div>
        </div>
    );
}

const StatusCard = ({ title, status, color }) => (
    <div style={{ padding: '1.5rem', backgroundColor: color, borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h3 style={{ margin: 0 }}>{title}</h3>
        <p style={{ fontSize: '1.5rem', fontWeight: 'bold', marginTop: '0.5rem', textTransform: 'uppercase' }}>{status || 'OFFLINE'}</p>
    </div>
);

export default Dashboard;
