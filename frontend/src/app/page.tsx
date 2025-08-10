'use client';
import { useEffect, useState } from 'react';

export default function Home() {
  const [status, setStatus] = useState<'loading'|'ok'|'error'>('loading');
  const [payload, setPayload] = useState<string>('');

  useEffect(() => {
    const url = `${process.env.NEXT_PUBLIC_API_URL}/health`;
    fetch(url)
      .then(r => r.json())
      .then(d => { setStatus('ok'); setPayload(JSON.stringify(d)); })
      .catch(() => setStatus('error'));
  }, []);

  return (
    <main style={{ padding: 24, fontFamily: 'ui-sans-serif, system-ui' }}>
      <h1 style={{ fontSize: 28, marginBottom: 12 }}>AI Logo Studio</h1>
      <p style={{ marginBottom: 8 }}>
        Backend health: <b>{status}</b>
      </p>
      {payload && <pre style={{ background: '#f5f5f5', padding: 12, borderRadius: 8 }}>{payload}</pre>}
    </main>
  );
}
