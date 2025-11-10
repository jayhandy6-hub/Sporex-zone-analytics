import React, {useEffect, useState} from 'react';

export default function App(){
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(()=> {
    const url = process.env.NEXT_PUBLIC_MATCHES_URL || '/matches_today.json';
    fetch(url).then(r=>r.json()).then(j=>{ setData(j); setLoading(false); }).catch(e=>{ console.error(e); setLoading(false); });
  }, []);

  if(loading) return <div style={{padding:20}}>Chargement...</div>;
  if(!data) return <div style={{padding:20}}>Aucune donnée.</div>;

  return (
    <div style={{background:'#000', color:'#fff', minHeight:'100vh', padding:20, fontFamily:'sans-serif'}}>
      <header style={{display:'flex', gap:12, alignItems:'center'}}>
        <div style={{width:56, height:56, borderRadius:12, background:'#0b0b0b', display:'flex', alignItems:'center', justifyContent:'center'}}>
          <svg width="36" height="36" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="64" height="64" rx="12" fill="#0B0B0B"/>
            <path d="M32 12L40.5 28H23.5L32 12Z" fill="#D4AF37"/>
            <path d="M22 36C22 30 26 26 32 26C38 26 42 30 42 36V46H22V36Z" fill="#D4AF37" opacity="0.95"/>
            <circle cx="32" cy="38" r="2.8" fill="#0B0B0B"/>
          </svg>
        </div>
        <div>
          <h1 style={{margin:0}}>SPOREX STATS</h1>
          <div style={{color:'#bbb', fontSize:13}}>Analyses & Prédictions — Filtre ≥ 80%</div>
        </div>
      </header>

      <main style={{marginTop:20}}>
        {data.signals && data.signals.length>0 ? (
          data.signals.map((s, i)=>(
            <div key={i} style={{border:'1px solid #222', padding:12, borderRadius:12, marginBottom:12, background:'#0b0b0b'}}>
              <div style={{display:'flex', justifyContent:'space-between'}}>
                <div>
                  <div style={{color:'#bbb', fontSize:13}}>{s.league} • {s.kickoff}</div>
                  <div style={{fontWeight:700, fontSize:18}}>{s.home} vs {s.away}</div>
                </div>
                <div style={{textAlign:'right'}}>
                  <div style={{color:'#D4AF37', fontWeight:800, fontSize:22}}>{Math.round(s.p_model*100)}%</div>
                  <div style={{color:'#bbb', fontSize:13}}>Cote ≈ {s.avg_odd}</div>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div style={{padding:20, color:'#bbb'}}>Aucun signal ≥ 80 % aujourd'hui.</div>
        )}
      </main>
    </div>
  );
}
