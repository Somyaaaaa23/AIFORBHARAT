import React, { useState, useEffect } from 'react';

function AuditLog() {
    const [logs, setLogs] = useState([]);

    useEffect(() => {
        fetch('http://localhost:8000/api/v1/audit/logs')
            .then(res => res.json())
            .then(data => setLogs(data));
    }, []);

    return (
        <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
            <h1>Audit Trail</h1>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
                {logs.map(log => (
                    <div key={log.id} style={{ border: '1px solid #ddd', padding: '1rem', borderRadius: '8px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <strong>{log.action}</strong>
                            <span style={{ color: log.status === 'SUCCESS' ? 'green' : 'red' }}>{log.status}</span>
                        </div>
                        <div style={{ fontSize: '0.875rem', color: '#666', marginTop: '0.5rem' }}>
                            UBID: {log.ubid} | Dept: {log.department_id} | {new Date(log.timestamp).toLocaleString()}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default AuditLog;
