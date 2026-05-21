import React from 'react';

// ── Design tokens ─────────────────────────────────────────────────────────────
const G = {
  dark:      '#1a6b3c',
  mid:       '#2e9b5a',
  light:     '#e8f5ee',
  lighter:   '#f4fdf7',
  accent:    '#43c97a',
  grafite:   '#1c2833',
  grafite2:  '#232f3e',
  gray:      '#f0f2f4',
  grayBorder:'#dde2e7',
  text:      '#1c2833',
  textMid:   '#4a5568',
  textLight: '#8fa0b0',
  white:     '#ffffff',
  red:       '#c0392b',
  amber:     '#d97706',
};

const WEEK = '2026-W21';
const DATE = 'May 19–25, 2026';

// ── Fake data ─────────────────────────────────────────────────────────────────
const EVENTS_DATA = {
  'Brazil Operations': { sir: ['1.24', '1.31'], rir: ['1.45', '1.52'], ltir: ['0.18', '0.22'], fair: ['0.09', '0.11'], highlight: true },
  'Fulfillment Centers': { sir: ['1.61', '1.41'], rir: ['1.61', '1.21'], ltir: ['0.00', '0.20'], fair: ['0.00', '0.10'] },
  'Sort Centers':        { sir: ['0.98', '1.10'], rir: ['0.86', '0.95'], ltir: ['0.00', '0.12'], fair: ['0.00', '0.00'] },
  'Logistics':           { sir: ['1.05', '1.22'], rir: ['1.12', '1.30'], ltir: ['0.20', '0.28'], fair: ['0.10', '0.14'] },
};

const BARRIERS_DATA = {
  'Brazil Operations': { dfy_rate: ['20.1', '17.4'], closure: ['83.2%', '85.0%'], insp_otc: ['91.3%', '88.7%'], near_miss: ['82', '1,240'], highlight: true },
  'Fulfillment Centers': { dfy_rate: ['22.5', '18.9'], closure: ['78.6%', '86.6%'], insp_otc: ['100%', '96.0%'], near_miss: ['5', '82'] },
  'Sort Centers':        { dfy_rate: ['18.2', '16.1'], closure: ['88.9%', '90.1%'], insp_otc: ['83.3%', '91.8%'], near_miss: ['2', '44'] },
  'Logistics':           { dfy_rate: ['17.4', '15.8'], closure: ['80.0%', '82.3%'], insp_otc: ['90.0%', '87.2%'], near_miss: ['12', '198'] },
};

const DFY_BEST = [
  {
    type: 'Fulfillment Center', typeBg: '#1a6b3c', typeColor: '#fff',
    site: 'GRU5', login: 'jsilva', obs: 8,
    text: 'Proactively identified hydraulic fluid leak on forklift during pre-trip inspection, preventing equipment failure and potential injury.',
    date: 'May 19',
  },
  {
    type: 'Fulfillment Center', typeBg: '#1a6b3c', typeColor: '#fff',
    site: 'CNF1', login: 'mferreira', obs: 5,
    text: 'Reported missing floor marking near conveyor belt, preventing pedestrian-PIT conflict before incident occurred.',
    date: 'May 18',
  },
  {
    type: 'Sort Center', typeBg: '#1565c0', typeColor: '#fff',
    site: 'CGH3', login: 'rcoelho', obs: 3,
    text: 'Identified broken dock leveler latch and raised emergency work order, avoiding potential fall-from-height event.',
    date: 'May 20',
  },
  {
    type: 'Logistics', typeBg: '#6f42c1', typeColor: '#fff',
    site: 'DSP3', login: 'abarros', obs: 11,
    text: 'Spotted improperly secured cargo load in yard truck, corrected before road transport, eliminating road safety risk.',
    date: 'May 17',
  },
];

// ── Shared style helpers ──────────────────────────────────────────────────────
const pill = (bg, color = '#fff', px = 16, py = 6) => ({
  display: 'inline-flex', alignItems: 'center', gap: 6,
  background: bg, color, borderRadius: 999,
  padding: `${py}px ${px}px`, fontWeight: 700, fontSize: 12, letterSpacing: 0.8,
  textTransform: 'uppercase',
});

const shadow = '0 2px 10px rgba(0,0,0,0.07)';
const card = (extra = {}) => ({
  background: G.white, borderRadius: 12, boxShadow: shadow,
  border: `1px solid ${G.grayBorder}`, ...extra,
});

// ── Sub-components ────────────────────────────────────────────────────────────
function SectionTitle({ icon, label }) {
  return (
    <div style={{ marginBottom: 18 }}>
      <span style={pill(G.grafite2, '#fff', 18, 8)}>
        {icon && <span style={{ fontSize: 14 }}>{icon}</span>}
        {label}
      </span>
    </div>
  );
}

function SnapshotItem({ icon, title, content, empty }) {
  return (
    <div style={{ ...card(), padding: 0, overflow: 'hidden', marginBottom: 14 }}>
      <div style={{ background: G.dark, padding: '10px 16px', display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{
          width: 32, height: 32, borderRadius: '50%',
          background: 'rgba(255,255,255,0.15)', display: 'flex', alignItems: 'center',
          justifyContent: 'center', fontSize: 16, flexShrink: 0,
        }}>{icon}</div>
        <span style={{ color: '#fff', fontWeight: 700, fontSize: 13, letterSpacing: 0.3 }}>{title}</span>
      </div>
      <div style={{ background: G.lighter, padding: '12px 16px', minHeight: 60, fontSize: 13, color: G.textMid, lineHeight: 1.55 }}>
        {empty
          ? <span style={{ color: G.textLight, fontStyle: 'italic' }}>No input this week.</span>
          : content}
      </div>
    </div>
  );
}

function DfyCard({ item }) {
  return (
    <div style={{ ...card({ borderLeft: `4px solid ${item.typeBg}` }), padding: '14px 16px', marginBottom: 12 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8, flexWrap: 'wrap' }}>
        <span style={{ ...pill(item.typeBg, item.typeColor, 10, 3), fontSize: 10 }}>{item.type}</span>
        <span style={{ fontWeight: 800, fontSize: 15, color: G.text }}>{item.site}</span>
        <span style={{ color: G.textLight, fontSize: 12 }}>·</span>
        <span style={{ color: G.textMid, fontSize: 12 }}>@{item.login}</span>
        <span style={{ color: G.textLight, fontSize: 12 }}>·</span>
        <span style={{ color: G.dark, fontWeight: 700, fontSize: 12 }}>✍️ {item.obs} obs.</span>
        <span style={{ marginLeft: 'auto', color: G.textLight, fontSize: 11 }}>{item.date}</span>
      </div>
      <div style={{ fontSize: 12.5, color: G.textMid, lineHeight: 1.55, borderTop: `1px solid ${G.grayBorder}`, paddingTop: 8 }}>
        {item.text}
      </div>
    </div>
  );
}

function MetricCard({ label, week, ytd, highlight }) {
  return (
    <div style={{
      ...card({
        borderLeft: `3px solid ${highlight ? G.dark : G.mid}`,
        background: highlight ? G.light : G.white,
      }),
      padding: '12px 14px', marginBottom: 10,
    }}>
      <div style={{ fontSize: 10.5, fontWeight: 600, color: G.textLight, textTransform: 'uppercase', letterSpacing: 0.6, marginBottom: 6 }}>
        {label}
      </div>
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
        <div style={{ fontSize: 26, fontWeight: 800, color: highlight ? G.dark : G.text, lineHeight: 1 }}>
          {week}
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: 9.5, color: G.textLight, fontWeight: 600, textTransform: 'uppercase' }}>YTD</div>
          <div style={{ fontSize: 14, fontWeight: 700, color: G.textMid }}>{ytd}</div>
        </div>
      </div>
    </div>
  );
}

function ColumnHeader({ label, highlight }) {
  return (
    <div style={{
      ...pill(highlight ? G.dark : G.grafite2, '#fff', 14, 7),
      marginBottom: 14, fontSize: 11, width: '100%', justifyContent: 'center',
      boxSizing: 'border-box',
    }}>
      {label}
    </div>
  );
}

function EventsColumn({ label, data, highlight }) {
  return (
    <div style={{ flex: 1, minWidth: 160 }}>
      <ColumnHeader label={label} highlight={highlight} />
      <MetricCard label="Serious Incident Rate (W)" week={data.sir[0]} ytd={data.sir[1]} highlight={highlight} />
      <MetricCard label="Recordable Incident Rate (W)" week={data.rir[0]} ytd={data.rir[1]} highlight={highlight} />
      <MetricCard label="Lost Time Incident Rate (W)" week={data.ltir[0]} ytd={data.ltir[1]} highlight={highlight} />
      <MetricCard label="First Aid Rate (W)" week={data.fair[0]} ytd={data.fair[1]} highlight={highlight} />
    </div>
  );
}

function BarriersColumn({ label, data, highlight }) {
  return (
    <div style={{ flex: 1, minWidth: 160 }}>
      <ColumnHeader label={label} highlight={highlight} />
      <MetricCard label="Dragonfly Rate (W)" week={data.dfy_rate[0]} ytd={data.dfy_rate[1]} highlight={highlight} />
      <MetricCard label="Dragonfly Closure Rate (W)" week={data.closure[0]} ytd={data.closure[1]} highlight={highlight} />
      <MetricCard label="Inspection OTC (W)" week={data.insp_otc[0]} ytd={data.insp_otc[1]} highlight={highlight} />
      <MetricCard label="Near Miss (W)" week={data.near_miss[0]} ytd={data.near_miss[1]} highlight={highlight} />
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────
export default function FlashReport() {
  return (
    <div style={{ background: G.gray, minHeight: '100vh', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif' }}>
      <div style={{ maxWidth: 1100, margin: '0 auto', padding: '0 0 40px 0' }}>

        {/* ── HEADER ── */}
        <div style={{
          background: G.grafite2, borderRadius: '0 0 16px 16px',
          padding: '24px 36px', marginBottom: 32,
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          boxShadow: '0 4px 20px rgba(0,0,0,0.18)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <div style={{
              width: 48, height: 48, borderRadius: 12,
              background: G.dark, display: 'flex', alignItems: 'center',
              justifyContent: 'center', fontSize: 22, boxShadow: `0 0 0 3px ${G.mid}`,
            }}>🛡️</div>
            <div>
              <div style={{ color: G.accent, fontSize: 11, fontWeight: 700, letterSpacing: 1.5, textTransform: 'uppercase', marginBottom: 2 }}>
                WHS Brazil
              </div>
              <div style={{ color: '#fff', fontSize: 28, fontWeight: 900, letterSpacing: -0.5, lineHeight: 1 }}>
                Flash Report
              </div>
              <div style={{ color: 'rgba(255,255,255,0.45)', fontSize: 12, marginTop: 3 }}>
                {DATE} · {WEEK}
              </div>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
            <div style={{
              background: 'rgba(255,255,255,0.06)', borderRadius: 10,
              padding: '8px 16px', textAlign: 'center', border: '1px solid rgba(255,255,255,0.1)',
            }}>
              <div style={{ color: G.accent, fontSize: 10, fontWeight: 700, letterSpacing: 1, textTransform: 'uppercase' }}>Safe to Go</div>
              <div style={{ color: '#fff', fontSize: 11, opacity: 0.6, marginTop: 2 }}>Safety First</div>
            </div>
            <div style={{
              background: 'rgba(255,255,255,0.06)', borderRadius: 10,
              padding: '8px 16px', textAlign: 'center', border: '1px solid rgba(255,255,255,0.1)',
            }}>
              <div style={{ color: '#ff9900', fontSize: 10, fontWeight: 700, letterSpacing: 1, textTransform: 'uppercase' }}>Amazon</div>
              <div style={{ color: '#fff', fontSize: 11, opacity: 0.6, marginTop: 2 }}>Operations</div>
            </div>
          </div>
        </div>

        <div style={{ padding: '0 24px' }}>

          {/* ── SNAPSHOT ── */}
          <SectionTitle icon="📸" label="Snapshot" />
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 36 }}>

            {/* Left */}
            <div>
              <SnapshotItem
                icon="💡"
                title="Did You Know?"
                content="In 2025, proactive near-miss reporting in Brazil Operations increased by 34%, directly contributing to a 12% reduction in recordable incidents. Every observation counts."
              />
              <SnapshotItem
                icon="🏆"
                title="Success Stories"
                content="GRU5 team reduced near-miss incidents by 40% after implementing new pedestrian barriers near dock doors — a direct result of associate-led safety initiatives this week."
              />
              <SnapshotItem
                icon="🚩"
                title="Hot Flag"
                content={<span><strong style={{ color: G.red }}>PIT-Pedestrian conflicts</strong> — 3 events registered across FC sites this week. Immediate refresher training recommended for dock associates. Escalated to site EHS leads.</span>}
              />
            </div>

            {/* Right — Best Dragonfly */}
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
                <span style={{ ...pill(G.dark, '#fff', 14, 7), fontSize: 11 }}>🐉 Best Dragonfly</span>
                <span style={{ fontSize: 11, color: G.textLight }}>Top observations · {WEEK}</span>
              </div>
              {DFY_BEST.map((item, i) => <DfyCard key={i} item={item} />)}
            </div>
          </div>

          {/* ── EVENTS ── */}
          <SectionTitle icon="⚠️" label="Events" />
          <div style={{ display: 'flex', gap: 20, marginBottom: 36, flexWrap: 'wrap' }}>
            {Object.entries(EVENTS_DATA).map(([label, data]) => (
              <EventsColumn key={label} label={label} data={data} highlight={!!data.highlight} />
            ))}
          </div>

          {/* ── BARRIERS ── */}
          <SectionTitle icon="🛡️" label="Barriers" />
          <div style={{ display: 'flex', gap: 20, marginBottom: 40, flexWrap: 'wrap' }}>
            {Object.entries(BARRIERS_DATA).map(([label, data]) => (
              <BarriersColumn key={label} label={label} data={data} highlight={!!data.highlight} />
            ))}
          </div>

          {/* ── FOOTER ── */}
          <div style={{
            background: G.grafite2, borderRadius: 16, padding: '20px 32px',
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            flexWrap: 'wrap', gap: 16, boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <div style={{
                width: 40, height: 40, borderRadius: 10,
                background: G.dark, display: 'flex', alignItems: 'center',
                justifyContent: 'center', fontSize: 18,
              }}>🛡️</div>
              <div>
                <div style={{ color: '#fff', fontWeight: 700, fontSize: 13 }}>WHS — Workplace Health & Safety</div>
                <div style={{ color: G.accent, fontSize: 11, fontWeight: 600, letterSpacing: 0.5, marginTop: 2 }}>
                  Engage · Enable · Inspire
                </div>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <span style={{ color: 'rgba(255,255,255,0.55)', fontSize: 13, fontStyle: 'italic' }}>
                Have you done your deep dive today?
              </span>
              <button style={{
                background: G.dark, color: '#fff', border: `2px solid ${G.mid}`,
                borderRadius: 999, padding: '6px 20px', fontWeight: 800, fontSize: 14,
                cursor: 'pointer', letterSpacing: 0.5,
              }}>Go!</button>
            </div>
            <div style={{ color: 'rgba(255,255,255,0.3)', fontSize: 11 }}>
              v1.0 · {DATE}
            </div>
          </div>

        </div>
      </div>

      {/* Print styles */}
      <style>{`
        @media print {
          body { background: #fff !important; }
          @page { margin: 1cm; size: A4 landscape; }
        }
      `}</style>
    </div>
  );
}
