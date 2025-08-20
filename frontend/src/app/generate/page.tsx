'use client';
import { useEffect, useRef, useState } from 'react';
import Progress from './Progress';

type Stage = 'queued' | 'generating' | 'vectorizing' | 'exporting' | 'done' | 'error' | 'not_found';

export default function GeneratePage() {
  const [businessType, setBusinessType] = useState('coffee shop');
  const [style, setStyle] = useState('minimal');
  const [colors, setColors] = useState('warm');
  const [jobId, setJobId] = useState<string | null>(null);
  const [stage, setStage] = useState<Stage | null>(null);
  const [log, setLog] = useState<string[]>([]);
  const [variants, setVariants] = useState<Array<{index:number; palette:any; svg:{url:string}}>>([]);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    return () => {
      if (esRef.current) esRef.current.close();
    };
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStage(null);
    setLog([]);
    setJobId(null);
    if (esRef.current) { esRef.current.close(); esRef.current = null; }

    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/generate`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        business_type: businessType,
        preferences: { style, colors }
      })
    });
    const data = await res.json();
    setJobId(data.job_id);
    setStage('queued');
    setLog((l) => [...l, `job created: ${data.job_id}`]);

    // Подписка на SSE
    const es = new EventSource(`${process.env.NEXT_PUBLIC_API_URL}/api/progress/${data.job_id}`);
    esRef.current = es;
    es.onmessage = (ev) => {
      try {
        const payload = JSON.parse(ev.data);
        if (payload.stage) {
          setStage(payload.stage);
          setLog((l) => [...l, `stage: ${payload.stage}`]);
          if (payload.stage === 'done') {
            fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/result/${data.job_id}`)
              .then(r => r.json())
              .then(r => setVariants(r?.variants ?? []))
              .catch(() => {});
          }
          if (payload.stage === 'done' || payload.stage === 'error' || payload.stage === 'not_found') {
            es.close();
            esRef.current = null;
          }
        }
      } catch {
        // игнорируем мусорные события
      }
    };
    es.onerror = () => {
      setLog((l) => [...l, 'SSE error']);
      es.close();
      esRef.current = null;
    };
  }

  return (
    <main style={{padding:24, maxWidth:720, margin:'0 auto', fontFamily:'ui-sans-serif, system-ui'}}>
      <h1 style={{fontSize:28, marginBottom:16}}>AI Logo Studio — Generate</h1>

      <form onSubmit={handleSubmit} style={{display:'grid', gap:12, marginBottom:24}}>
        <label>
          <div>Business type</div>
          <input value={businessType} onChange={e=>setBusinessType(e.target.value)}
                 style={{border:'1px solid #ddd', padding:8, borderRadius:8, width:'100%'}} />
        </label>
        <label>
          <div>Style</div>
          <input value={style} onChange={e=>setStyle(e.target.value)}
                 style={{border:'1px solid #ddd', padding:8, borderRadius:8, width:'100%'}} />
        </label>
        <label>
          <div>Colors</div>
          <input value={colors} onChange={e=>setColors(e.target.value)}
                 style={{border:'1px solid #ddd', padding:8, borderRadius:8, width:'100%'}} />
        </label>
        <button type="submit" style={{padding:'10px 14px', borderRadius:10, border:'1px solid #222'}}>
          Create job
        </button>
      </form>

      <div style={{marginBottom:8}}>
        <b>Job:</b> {jobId ?? '—'}
      </div>
      <div style={{marginBottom:16}}>
        <b>Stage:</b> {stage ?? '—'}
      </div>

      <Progress stage={stage} />

      {variants.length > 0 && (
        <>
          <h3 style={{margin: '12px 0'}}>Variants</h3>
          <div style={{display:'grid', gap:12, gridTemplateColumns:'repeat(auto-fill, minmax(180px, 1fr))'}}>
            {variants.map(v => (
              <a key={v.index} href={v.svg.url} target="_blank" rel="noreferrer"
                 style={{display:'block', border:'1px solid #eee', borderRadius:8, padding:8}}>
                <div style={{fontSize:12, opacity:0.7, marginBottom:6}}>
                  #{v.index} • {v.palette?.name ?? 'palette'}
                </div>
                <img src={v.svg.url} alt={`variant ${v.index}`} style={{width:'100%', height:160, objectFit:'contain'}} />
              </a>
            ))}
          </div>
        </>
      )}

      <details open>
        <summary>Log</summary>
        <pre style={{background:'#f7f7f8', padding:12, borderRadius:8, whiteSpace:'pre-wrap'}}>
          {log.join('\n')}
        </pre>
      </details>
    </main>
  );
}
