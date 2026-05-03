import React, { useState, useEffect } from 'react';

function ConflictReview() {
    const [conflicts, setConflicts] = useState([]);

    useEffect(() => {
        fetch('http://localhost:8000/api/v1/conflict/pending')
            .then(res => res.json())
            .then(data => setConflicts(data));
    }, []);

    return (
        <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
            <h1>Conflict Review</h1>
            <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '1rem' }}>
                <thead>
                    <tr style={{ backgroundColor: '#f3f4f6' }}>
                        <th style={cellStyle}>UBID</th>
                        <th style={cellStyle}>Field</th>
                        <th style={cellStyle}>SWS Value</th>
                        <th style={cellStyle}>Dept Value</th>
                        <th style={cellStyle}>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {conflicts.map(c => (
                        <tr key={c.id}>
                            <td style={cellStyle}>{c.ubid}</td>
                            <td style={cellStyle}>{c.field}</td>
                            <td style={cellStyle}>{c.sws_value}</td>
                            <td style={cellStyle}>{c.dept_value}</td>
                            <td style={cellStyle}>
                                <button style={btnStyle('green')}>Keep SWS</button>
                                <button style={btnStyle('blue')}>Keep Dept</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

const cellStyle = { border: '1px solid #e5e7eb', padding: '12px', textAlign: 'left' };
const btnStyle = (color) => ({
    backgroundColor: color,
    color: 'white',
    border: 'none',
    padding: '6px 12px',
    borderRadius: '4px',
    marginRight: '8px',
    cursor: 'pointer'
});

export default ConflictReview;
