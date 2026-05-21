import React, { useEffect, useState } from 'react';

const SAMPLE = [
  {
    Site: 'GRU5', BU: 'LATAMCF', Sub_BU: 'GCF', Week: '2026-W21',
    Year: 'FY2026', Quarter: 'Q2', Month: '2026-05',
    Manual_Success_Story: 'Team reduced near-miss incidents by 40% after implementing new pedestrian barriers near dock doors.',
    Manual_Tip: 'Always verify PIT battery levels at shift start — low batteries caused 2 near-misses this week.',
    Manual_Submitted_By: 'paulosjr',
    Total_Hours_Week: '12,450', Total_Hours_YTD: '198,320',
    INC_All_Week: '3', INC_All_YTD: '47', INC_SI_Week: '1', INC_SI_YTD: '14',
    INC_RI_Week: '1', INC_RI_YTD: '12', INC_DART_Week: '0', INC_DART_YTD: '5',
    INC_LTI_Week: '0', INC_LTI_YTD: '2', INC_FAI_Week: '0', INC_FAI_YTD: '1',
    INC_MSD_RI_Week: '0', INC_MSD_RI_YTD: '3', INC_MSD_LTI_Week: '0',
    INC_Near_Miss_Week: '5', INC_Near_Miss_YTD: '82',
    INC_PIT_All_Week: '1', INC_PIT_SI_Week: '0', INC_PIT_RI_Week: '1', INC_Yard_Week: '0', INC_PIT_Ped_Week: '0',
    INC_RIR_Week: '1.61', INC_RIR_YTD: '1.21', INC_SIR_Week: '1.61', INC_SIR_YTD: '1.41',
    INC_DART_Rate_Week: '0.00', INC_DART_Rate_YTD: '0.50', INC_LTIR_Week: '0.00', INC_LTIR_YTD: '0.20',
    INC_MSD_RIR_Week: '0.00', INC_MSD_RIR_YTD: '0.30', INC_FAIR_Week: '0.00', INC_FAIR_YTD: '0.10',
    INSP_Due_Insp_Week: '8', INSP_Due_Insp_YTD: '124', INSP_OTC_Week: '8', INSP_OTC_YTD: '119',
    INSP_Due_Tasks_Week: '22', INSP_Due_Tasks_YTD: '341', INSP_Task_OTC_Week: '20', INSP_Task_OTC_YTD: '310',
    INSP_On_Time_Week: '8', INSP_On_Time_YTD: '119', INSP_Overdue_Week: '0', INSP_Overdue_YTD: '5',
    INSP_Tasks_On_Time_Week: '20', INSP_Tasks_On_Time_YTD: '310', INSP_Tasks_Overdue_Week: '2', INSP_Tasks_Overdue_YTD: '31',
    DFY_Total_Obs_Week: '14', DFY_Total_Obs_YTD: '187', DFY_Closed_Week: '11', DFY_Closed_YTD: '162',
    DFY_Open_Week: '3', DFY_Open_YTD: '25', DFY_Closure_Rate_Week: '78.6%', DFY_Closure_Rate_YTD: '86.6%',
    DFY_Feedback_Rate_Week: '71.4%', DFY_Feedback_Rate_YTD: '74.3%',
    DFY_First_Timers_Week: '4', DFY_First_Timers_YTD: '53',
    DFY_Sentiment_Positive_Pct_Week: '64.3%', DFY_Sentiment_Positive_Pct_YTD: '61.0%',
    DFY_QRI_Avg_Week: '3.8', DFY_QRI_Avg_YTD: '3.6',
    DFY_Days_Completion_Avg_Week: '4.2', DFY_Days_Completion_Avg_YTD: '5.1',
    DFY_Days_Response_Avg_Week: '1.1', DFY_Days_Response_Avg_YTD: '1.4',
    DFY_Rate_Week: '22.49', DFY_Rate_YTD: '18.86',
    DFY_Submitter_Rate_Week: '12.85', DFY_Submitter_Rate_YTD: '11.20',
    DFY_Description: '📦 GRU5       👤 @jsilva       ✍️ 8 obs.\n\nObserved forklift operator performing pre-trip inspection proactively before shift start, identifying a hydraulic fluid leak that could have caused equipment failure.\n\n💪 Above and beyond! Recognize them: https://atoz.amazon.work/shout-outs',
    DFY_Date: '2026-05-19',
  },
  {
    Site: 'CNF1', BU: 'LATAMCF', Sub_BU: 'GCF', Week: '2026-W21',
    Year: 'FY2026', Quarter: 'Q2', Month: '2026-05',
    Manual_Success_Story: '',
    Manual_Tip: '',
    Manual_Submitted_By: '',
    Total_Hours_Week: '9,870', Total_Hours_YTD: '162,500',
    INC_All_Week: '1', INC_All_YTD: '28', INC_SI_Week: '0', INC_SI_YTD: '8',
    INC_RI_Week: '0', INC_RI_YTD: '7', INC_DART_Week: '0', INC_DART_YTD: '2',
    INC_LTI_Week: '0', INC_LTI_YTD: '1', INC_FAI_Week: '0', INC_FAI_YTD: '0',
    INC_MSD_RI_Week: '0', INC_MSD_RI_YTD: '1', INC_MSD_LTI_Week: '0',
    INC_Near_Miss_Week: '2', INC_Near_Miss_YTD: '44',
    INC_PIT_All_Week: '0', INC_PIT_SI_Week: '0', INC_PIT_RI_Week: '0', INC_Yard_Week: '1', INC_PIT_Ped_Week: '0',
    INC_RIR_Week: '0.00', INC_RIR_YTD: '0.86', INC_SIR_Week: '0.00', INC_SIR_YTD: '0.98',
    INC_DART_Rate_Week: '0.00', INC_DART_Rate_YTD: '0.25', INC_LTIR_Week: '0.00', INC_LTIR_YTD: '0.12',
    INC_MSD_RIR_Week: '0.00', INC_MSD_RIR_YTD: '0.12', INC_FAIR_Week: '0.00', INC_FAIR_YTD: '0.00',
    INSP_Due_Insp_Week: '6', INSP_Due_Insp_YTD: '98', INSP_OTC_Week: '5', INSP_OTC_YTD: '90',
    INSP_Due_Tasks_Week: '15', INSP_Due_Tasks_YTD: '245', INSP_Task_OTC_Week: '14', INSP_Task_OTC_YTD: '228',
    INSP_On_Time_Week: '5', INSP_On_Time_YTD: '90', INSP_Overdue_Week: '1', INSP_Overdue_YTD: '8',
    INSP_Tasks_On_Time_Week: '14', INSP_Tasks_On_Time_YTD: '228', INSP_Tasks_Overdue_Week: '1', INSP_Tasks_Overdue_YTD: '17',
    DFY_Total_Obs_Week: '9', DFY_Total_Obs_YTD: '121', DFY_Closed_Week: '8', DFY_Closed_YTD: '109',
    DFY_Open_Week: '1', DFY_Open_YTD: '12', DFY_Closure_Rate_Week: '88.9%', DFY_Closure_Rate_YTD: '90.1%',
    DFY_Feedback_Rate_Week: '77.8%', DFY_Feedback_Rate_YTD: '80.2%',
    DFY_First_Timers_Week: '2', DFY_First_Timers_YTD: '31',
    DFY_Sentiment_Positive_Pct_Week: '55.6%', DFY_Sentiment_Positive_Pct_YTD: '58.7%',
    DFY_QRI_Avg_Week: '4.1', DFY_QRI_Avg_YTD: '3.9',
    DFY_Days_Completion_Avg_Week: '3.5', DFY_Days_Completion_Avg_YTD: '4.8',
    DFY_Days_Response_Avg_Week: '0.9', DFY_Days_Response_Avg_YTD: '1.2',
    DFY_Rate_Week: '18.24', DFY_Rate_YTD: '14.89',
    DFY_Submitter_Rate_Week: '10.13', DFY_Submitter_Rate_YTD: '9.60',
    DFY_Description: '📦 CNF1       👤 @mferreira       ✍️ 5 obs.\n\nAssociate identified missing floor marking near conveyor belt and immediately reported to safety team, preventing potential pedestrian incident.',
    DFY_Date: '2026-05-18',
  },
];

const colors = {
  manual: { header: '#6f42c1', light: '#f3f0ff', border: '#d4b8ff' },
  inc:    { header: '#c0392b', light: '#fff5f5', border: '#ffb3b3' },
  insp:   { header: '#1a6b3c', light: '#f0fff6', border: '#a3ddb8' },
  dfy:    { header: '#1565c0', light: '#f0f6ff', border: '#a3c4f5' },
  id:     { header: '#232f3e', light: '#f5f6f7', border: '#c8cdd2' },
};

const SECTIONS = [
  {
    key: 'id', label: 'Identification',
    cols: [
      { label: 'Site', field: 'Site' }, { label: 'BU', field: 'BU' }, { label: 'Sub BU', field: 'Sub_BU' },
      { label: 'Week', field: 'Week' }, { label: 'Year', field: 'Year' },
      { label: 'Quarter', field: 'Quarter' }, { label: 'Month', field: 'Month' },
    ],
  },
  {
    key: 'manual', label: 'Manual Input',
    cols: [
      { label: 'Success Story', field: 'Manual_Success_Story', wide: true },
      { label: 'Tip', field: 'Manual_Tip', wide: true },
      { label: 'Submitted By', field: 'Manual_Submitted_By' },
    ],
  },
  {
    key: 'inc', label: 'Incidents',
    cols: [
      { label: 'Hours W', field: 'Total_Hours_Week' }, { label: 'Hours YTD', field: 'Total_Hours_YTD' },
      { label: 'All W', field: 'INC_All_Week' }, { label: 'All YTD', field: 'INC_All_YTD' },
      { label: 'SI W', field: 'INC_SI_Week' }, { label: 'SI YTD', field: 'INC_SI_YTD' },
      { label: 'RI W', field: 'INC_RI_Week' }, { label: 'RI YTD', field: 'INC_RI_YTD' },
      { label: 'DART W', field: 'INC_DART_Week' }, { label: 'DART YTD', field: 'INC_DART_YTD' },
      { label: 'LTI W', field: 'INC_LTI_Week' }, { label: 'LTI YTD', field: 'INC_LTI_YTD' },
      { label: 'FAI W', field: 'INC_FAI_Week' }, { label: 'FAI YTD', field: 'INC_FAI_YTD' },
      { label: 'MSD RI W', field: 'INC_MSD_RI_Week' }, { label: 'MSD RI YTD', field: 'INC_MSD_RI_YTD' },
      { label: 'MSD LTI W', field: 'INC_MSD_LTI_Week' },
      { label: 'Near Miss W', field: 'INC_Near_Miss_Week' }, { label: 'Near Miss YTD', field: 'INC_Near_Miss_YTD' },
      { label: 'PIT All W', field: 'INC_PIT_All_Week' }, { label: 'PIT SI W', field: 'INC_PIT_SI_Week' },
      { label: 'PIT RI W', field: 'INC_PIT_RI_Week' }, { label: 'Yard W', field: 'INC_Yard_Week' },
      { label: 'PIT Ped W', field: 'INC_PIT_Ped_Week' },
      { label: 'RIR W', field: 'INC_RIR_Week', rate: true }, { label: 'RIR YTD', field: 'INC_RIR_YTD', rate: true },
      { label: 'SIR W', field: 'INC_SIR_Week', rate: true }, { label: 'SIR YTD', field: 'INC_SIR_YTD', rate: true },
      { label: 'DART Rate W', field: 'INC_DART_Rate_Week', rate: true }, { label: 'DART Rate YTD', field: 'INC_DART_Rate_YTD', rate: true },
      { label: 'LTIR W', field: 'INC_LTIR_Week', rate: true }, { label: 'LTIR YTD', field: 'INC_LTIR_YTD', rate: true },
      { label: 'MSD RIR W', field: 'INC_MSD_RIR_Week', rate: true }, { label: 'MSD RIR YTD', field: 'INC_MSD_RIR_YTD', rate: true },
      { label: 'FAIR W', field: 'INC_FAIR_Week', rate: true }, { label: 'FAIR YTD', field: 'INC_FAIR_YTD', rate: true },
    ],
  },
  {
    key: 'insp', label: 'Inspections',
    cols: [
      { label: 'Due Insp W', field: 'INSP_Due_Insp_Week' }, { label: 'Due Insp YTD', field: 'INSP_Due_Insp_YTD' },
      { label: 'OTC W', field: 'INSP_OTC_Week' }, { label: 'OTC YTD', field: 'INSP_OTC_YTD' },
      { label: 'Due Tasks W', field: 'INSP_Due_Tasks_Week' }, { label: 'Due Tasks YTD', field: 'INSP_Due_Tasks_YTD' },
      { label: 'Task OTC W', field: 'INSP_Task_OTC_Week' }, { label: 'Task OTC YTD', field: 'INSP_Task_OTC_YTD' },
      { label: 'On Time W', field: 'INSP_On_Time_Week' }, { label: 'On Time YTD', field: 'INSP_On_Time_YTD' },
      { label: 'Overdue W', field: 'INSP_Overdue_Week' }, { label: 'Overdue YTD', field: 'INSP_Overdue_YTD' },
      { label: 'Tasks On Time W', field: 'INSP_Tasks_On_Time_Week' }, { label: 'Tasks On Time YTD', field: 'INSP_Tasks_On_Time_YTD' },
      { label: 'Tasks Overdue W', field: 'INSP_Tasks_Overdue_Week' }, { label: 'Tasks Overdue YTD', field: 'INSP_Tasks_Overdue_YTD' },
    ],
  },
  {
    key: 'dfy', label: 'Dragonfly',
    cols: [
      { label: 'Total Obs W', field: 'DFY_Total_Obs_Week' }, { label: 'Total Obs YTD', field: 'DFY_Total_Obs_YTD' },
      { label: 'Closed W', field: 'DFY_Closed_Week' }, { label: 'Closed YTD', field: 'DFY_Closed_YTD' },
      { label: 'Open W', field: 'DFY_Open_Week' }, { label: 'Open YTD', field: 'DFY_Open_YTD' },
      { label: 'Closure Rate W', field: 'DFY_Closure_Rate_Week', rate: true }, { label: 'Closure Rate YTD', field: 'DFY_Closure_Rate_YTD', rate: true },
      { label: 'Feedback Rate W', field: 'DFY_Feedback_Rate_Week', rate: true }, { label: 'Feedback Rate YTD', field: 'DFY_Feedback_Rate_YTD', rate: true },
      { label: 'First Timers W', field: 'DFY_First_Timers_Week' }, { label: 'First Timers YTD', field: 'DFY_First_Timers_YTD' },
      { label: 'Positive Sent W', field: 'DFY_Sentiment_Positive_Pct_Week', rate: true }, { label: 'Positive Sent YTD', field: 'DFY_Sentiment_Positive_Pct_YTD', rate: true },
      { label: 'QRI Avg W', field: 'DFY_QRI_Avg_Week', rate: true }, { label: 'QRI Avg YTD', field: 'DFY_QRI_Avg_YTD', rate: true },
      { label: 'Days Comp W', field: 'DFY_Days_Completion_Avg_Week' }, { label: 'Days Comp YTD', field: 'DFY_Days_Completion_Avg_YTD' },
      { label: 'Days Resp W', field: 'DFY_Days_Response_Avg_Week' }, { label: 'Days Resp YTD', field: 'DFY_Days_Response_Avg_YTD' },
      { label: 'DFY Rate W', field: 'DFY_Rate_Week', rate: true }, { label: 'DFY Rate YTD', field: 'DFY_Rate_YTD', rate: true },
      { label: 'Submitter Rate W', field: 'DFY_Submitter_Rate_Week', rate: true }, { label: 'Submitter Rate YTD', field: 'DFY_Submitter_Rate_YTD', rate: true },
      { label: 'Description', field: 'DFY_Description', wide: true },
      { label: 'Date', field: 'DFY_Date' },
    ],
  },
];

const s = {
  wrap: { fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif', fontSize: 13 },
  siteCard: { background: '#fff', borderRadius: 10, marginBottom: 32, boxShadow: '0 2px 8px rgba(0,0,0,0.08)', overflow: 'hidden' },
  siteHeader: { background: '#232f3e', color: '#fff', padding: '14px 20px', display: 'flex', alignItems: 'center', gap: 16 },
  siteName: { fontSize: 20, fontWeight: 800, letterSpacing: 1 },
  siteMeta: { fontSize: 12, opacity: 0.7 },
  section: (c) => ({ borderTop: `3px solid ${c.header}` }),
  sectionHeader: (c) => ({
    background: c.header, color: '#fff', padding: '7px 16px',
    fontSize: 11, fontWeight: 700, letterSpacing: 1, textTransform: 'uppercase',
  }),
  grid: { display: 'flex', flexWrap: 'wrap', padding: '12px 16px', gap: 10 },
  cell: (c, wide) => ({
    background: c.light, border: `1px solid ${c.border}`, borderRadius: 6,
    padding: '8px 12px', minWidth: wide ? 260 : 90, maxWidth: wide ? 400 : 130,
    flex: wide ? '1 1 260px' : '0 0 auto',
  }),
  cellLabel: { fontSize: 10, color: '#888', fontWeight: 600, textTransform: 'uppercase', marginBottom: 3 },
  cellValue: (rate, empty) => ({
    fontSize: 13, fontWeight: 600,
    color: empty ? '#ccc' : rate ? '#1a6b3c' : '#232f3e',
    whiteSpace: 'pre-wrap', wordBreak: 'break-word',
  }),
};

function SiteCard({ row }) {
  const c = colors;
  return (
    <div style={s.siteCard}>
      <div style={s.siteHeader}>
        <div>
          <div style={s.siteName}>{row.Site}</div>
          <div style={s.siteMeta}>{row.BU} · {row.Sub_BU} · {row.Week}</div>
        </div>
        <div style={{ marginLeft: 'auto', textAlign: 'right', opacity: 0.7, fontSize: 12 }}>
          <div>{row.Year} / {row.Quarter} / {row.Month}</div>
          <div>{row.Total_Hours_Week} hrs this week</div>
        </div>
      </div>

      {SECTIONS.map((sec) => (
        <div key={sec.key} style={s.section(c[sec.key])}>
          <div style={s.sectionHeader(c[sec.key])}>{sec.label}</div>
          <div style={s.grid}>
            {sec.cols.map((col) => {
              const val = row[col.field];
              const empty = val === '' || val === undefined || val === null;
              return (
                <div key={col.field} style={s.cell(c[sec.key], col.wide)}>
                  <div style={s.cellLabel}>{col.label}</div>
                  <div style={s.cellValue(col.rate, empty)}>
                    {empty ? '—' : val}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}

export default function PreviewReport() {
  return (
    <div style={s.wrap}>
      <div style={{ marginBottom: 24, padding: '16px 0' }}>
        <div style={{ fontSize: 18, fontWeight: 700, color: '#232f3e' }}>Output Preview — output_flash_report.csv</div>
        <div style={{ fontSize: 13, color: '#888', marginTop: 4 }}>Sample data · Week 2026-W21 · 2 sites</div>
      </div>
      {SAMPLE.map((row) => <SiteCard key={row.Site} row={row} />)}
    </div>
  );
}
