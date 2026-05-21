import React, { useEffect, useState } from 'react';

const s = {
  card: {
    background: '#fff', borderRadius: 10, padding: '32px 36px',
    boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
  },
  headerRow: {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    marginBottom: 24, flexWrap: 'wrap', gap: 12,
  },
  h2: { fontSize: 20, fontWeight: 700, color: '#232f3e' },
  weekSelect: {
    padding: '8px 12px', borderRadius: 6, border: '1px solid #d4d4d4',
    fontSize: 14, background: '#fafafa',
  },
  empty: { color: '#888', textAlign: 'center', padding: '40px 0' },
  table: { width: '100%', borderCollapse: 'collapse', fontSize: 13 },
  th: {
    background: '#232f3e', color: '#fff', padding: '10px 12px',
    textAlign: 'left', fontWeight: 600,
  },
  td: { padding: '10px 12px', borderBottom: '1px solid #eee', verticalAlign: 'top' },
  tdAlt: {
    padding: '10px 12px', borderBottom: '1px solid #eee',
    verticalAlign: 'top', background: '#fafafa',
  },
  badge: {
    display: 'inline-block', padding: '2px 8px', borderRadius: 12,
    background: '#ff9900', color: '#232f3e', fontWeight: 700, fontSize: 11,
  },
};

export default function ViewEntries() {
  const [weeks, setWeeks] = useState([]);
  const [selectedWeek, setSelectedWeek] = useState('');
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    Promise.all([
      fetch('/api/weeks').then((r) => r.json()),
      fetch('/api/week').then((r) => r.json()),
    ]).then(([weeksData, currentWeekData]) => {
      const allWeeks = weeksData.weeks || [];
      const current = currentWeekData.week;
      if (!allWeeks.includes(current)) allWeeks.unshift(current);
      setWeeks(allWeeks);
      setSelectedWeek(current);
    });
  }, []);

  useEffect(() => {
    if (!selectedWeek) return;
    setLoading(true);
    fetch(`/api/entries?week=${encodeURIComponent(selectedWeek)}`)
      .then((r) => r.json())
      .then((d) => setEntries(d.entries || []))
      .finally(() => setLoading(false));
  }, [selectedWeek]);

  return (
    <div style={s.card}>
      <div style={s.headerRow}>
        <h2 style={s.h2}>
          Entries{' '}
          {entries.length > 0 && <span style={s.badge}>{entries.length}</span>}
        </h2>
        <select
          style={s.weekSelect}
          value={selectedWeek}
          onChange={(e) => setSelectedWeek(e.target.value)}
        >
          {weeks.map((w) => (
            <option key={w} value={w}>{w}</option>
          ))}
        </select>
      </div>

      {loading && <div style={s.empty}>Loading…</div>}

      {!loading && entries.length === 0 && (
        <div style={s.empty}>No entries for {selectedWeek}</div>
      )}

      {!loading && entries.length > 0 && (
        <div style={{ overflowX: 'auto' }}>
          <table style={s.table}>
            <thead>
              <tr>
                <th style={s.th}>Site</th>
                <th style={s.th}>Success Story</th>
                <th style={s.th}>Tip</th>
                <th style={s.th}>Submitted By</th>
                <th style={s.th}>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry, i) => {
                const cell = i % 2 === 0 ? s.td : s.tdAlt;
                return (
                  <tr key={i}>
                    <td style={{ ...cell, fontWeight: 700 }}>{entry.Site}</td>
                    <td style={cell}>{entry.Success_Story}</td>
                    <td style={cell}>{entry.Tip}</td>
                    <td style={{ ...cell, color: '#555' }}>{entry.Submitted_By}</td>
                    <td style={{ ...cell, color: '#888', whiteSpace: 'nowrap' }}>
                      {entry.Timestamp}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
