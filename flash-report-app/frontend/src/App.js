import React, { useState } from 'react';
import SubmitForm from './SubmitForm';
import ViewEntries from './ViewEntries';
import PreviewReport from './PreviewReport';
import FlashReport from './FlashReport';

const styles = {
  container: { minHeight: '100vh', background: '#f0f2f5' },
  header: {
    background: '#232f3e',
    color: '#fff',
    padding: '16px 32px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  title: { fontSize: 20, fontWeight: 700, letterSpacing: 0.5 },
  nav: { display: 'flex', gap: 8 },
  navBtn: (active) => ({
    padding: '8px 20px',
    borderRadius: 6,
    border: 'none',
    cursor: 'pointer',
    fontWeight: 600,
    fontSize: 14,
    background: active ? '#ff9900' : 'rgba(255,255,255,0.12)',
    color: active ? '#232f3e' : '#fff',
    transition: 'all 0.15s',
  }),
  content: { maxWidth: 860, margin: '0 auto', padding: '32px 16px' },
};

export default function App() {
  const [tab, setTab] = useState('submit');

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <span style={styles.title}>Flash Report — Site Input</span>
        <nav style={styles.nav}>
          <button style={styles.navBtn(tab === 'submit')} onClick={() => setTab('submit')}>
            Submit
          </button>
          <button style={styles.navBtn(tab === 'view')} onClick={() => setTab('view')}>
            View Entries
          </button>
          <button style={styles.navBtn(tab === 'preview')} onClick={() => setTab('preview')}>
            Output Preview
          </button>
          <button style={styles.navBtn(tab === 'flash')} onClick={() => setTab('flash')}>
            Flash Report
          </button>
        </nav>
      </header>
      <main style={styles.content}>
        {tab === 'submit' && <SubmitForm />}
        {tab === 'view' && <ViewEntries />}
        {tab === 'preview' && <PreviewReport />}
        {tab === 'flash' && <FlashReport />}
      </main>
    </div>
  );
}
