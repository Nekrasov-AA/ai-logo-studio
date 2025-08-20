'use client';

const ORDER = ['queued','generating','vectorizing','exporting','done'] as const;

export default function Progress({ stage }: { stage: string | null }) {
  const idx = stage ? ORDER.indexOf(stage as any) : -1;
  const pct = idx >= 0 ? ((idx + 1) / ORDER.length) * 100 : 0;

  return (
    <div style={{ margin: '12px 0 20px' }}>
      <div style={{ background: '#eee', height: 10, borderRadius: 8, overflow: 'hidden' }}>
        <div style={{ width: `${pct}%`, height: '100%' }} />
      </div>
      <div style={{ fontSize: 12, marginTop: 6, opacity: 0.75 }}>
        {stage ? `Stage: ${stage} (${Math.round(pct)}%)` : 'Waiting…'}
      </div>
    </div>
  );
}
