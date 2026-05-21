import React, { useEffect, useState } from 'react';

const s = {
  card: {
    background: '#fff',
    borderRadius: 10,
    padding: '32px 36px',
    boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
  },
  h2: { fontSize: 20, fontWeight: 700, marginBottom: 24, color: '#232f3e' },
  row: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 },
  field: { display: 'flex', flexDirection: 'column', gap: 6 },
  label: { fontSize: 13, fontWeight: 600, color: '#555' },
  select: {
    padding: '10px 12px', borderRadius: 6, border: '1px solid #d4d4d4',
    fontSize: 14, background: '#fafafa',
  },
  input: {
    padding: '10px 12px', borderRadius: 6, border: '1px solid #d4d4d4',
    fontSize: 14, background: '#f5f5f5', color: '#666',
  },
  textarea: {
    padding: '10px 12px', borderRadius: 6, border: '1px solid #d4d4d4',
    fontSize: 14, resize: 'vertical', minHeight: 100, fontFamily: 'inherit',
    background: '#fafafa',
  },
  btn: {
    marginTop: 8, padding: '12px 32px', background: '#ff9900', border: 'none',
    borderRadius: 6, fontWeight: 700, fontSize: 15, cursor: 'pointer', color: '#232f3e',
  },
  success: {
    marginTop: 16, padding: '14px 16px', background: '#d4edda', borderRadius: 6,
    color: '#155724', fontSize: 14,
  },
  error: {
    marginTop: 16, padding: '14px 16px', background: '#f8d7da', borderRadius: 6,
    color: '#721c24', fontSize: 14,
  },
};

export default function SubmitForm() {
  const [sites, setSites] = useState([]);
  const [site, setSite] = useState('');
  const [week, setWeek] = useState('');
  const [successStory, setSuccessStory] = useState('');
  const [tip, setTip] = useState('');
  const [status, setStatus] = useState(null); // null | 'ok' | 'error'
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch('/api/sites').then((r) => r.json()).then((d) => {
      setSites(d.sites);
      setSite(d.sites[0] || '');
    });
    fetch('/api/week').then((r) => r.json()).then((d) => setWeek(d.week));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus(null);
    try {
      const res = await fetch('/api/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          site,
          week,
          success_story: successStory,
          tip,
        }),
      });
      const data = await res.json();
      if (res.ok) {
        setStatus('ok');
        setMessage(`Submitted by ${data.submitted_by} at ${data.timestamp}`);
        setSuccessStory('');
        setTip('');
      } else {
        setStatus('error');
        setMessage(data.detail || 'Submission failed');
      }
    } catch (err) {
      setStatus('error');
      setMessage('Network error — check if the backend is running');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={s.card}>
      <h2 style={s.h2}>Submit Weekly Input</h2>
      <form onSubmit={handleSubmit}>
        <div style={s.row}>
          <div style={s.field}>
            <label style={s.label}>Site</label>
            <select style={s.select} value={site} onChange={(e) => setSite(e.target.value)} required>
              {sites.map((st) => (
                <option key={st} value={st}>{st}</option>
              ))}
            </select>
          </div>
          <div style={s.field}>
            <label style={s.label}>Week</label>
            <input style={s.input} value={week} readOnly />
          </div>
        </div>
        <div style={{ ...s.field, marginBottom: 16 }}>
          <label style={s.label}>Success Story</label>
          <textarea
            style={s.textarea}
            placeholder="Describe a success story from this week..."
            value={successStory}
            onChange={(e) => setSuccessStory(e.target.value)}
            required
          />
        </div>
        <div style={{ ...s.field, marginBottom: 24 }}>
          <label style={s.label}>Tip</label>
          <textarea
            style={s.textarea}
            placeholder="Share a useful tip or best practice..."
            value={tip}
            onChange={(e) => setTip(e.target.value)}
            required
          />
        </div>
        <button style={s.btn} type="submit" disabled={loading}>
          {loading ? 'Submitting…' : 'Submit'}
        </button>
        {status === 'ok' && <div style={s.success}>✓ {message}</div>}
        {status === 'error' && <div style={s.error}>✗ {message}</div>}
      </form>
    </div>
  );
}
