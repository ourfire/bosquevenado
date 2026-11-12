/* Motor del plano de la etapa 3 de Bosque Venado.
   Genera la geometría (lotes de 200 m² en clusters, calle, caminos verdes, bloques comunes)
   y los SVG del sitio. Lo usa src/build.py con: node src/engine.js
   La misma función calc() vive en el trazador interactivo. */
"use strict";
const YN0=268.306107, SN=(285.709928-268.306107)/88.431197, SS=26.299639/88.431197;
const COSN=Math.cos(Math.atan(SN)), COSS=Math.cos(Math.atan(SS));
const fmt=(n,d=0)=>Number(n).toLocaleString("es-MX",{minimumFractionDigits:d,maximumFractionDigits:d});
function parseSeq(s){ const v=String(s||"").split(/[^0-9]+/).map(Number).filter(n=>n>=1&&n<=64); return v.length?v:[1]; }

// Diseño elegido: calle central ondulada, clusters de 8, 4 y 2 con caminos verdes de 4 m, centro de energía y agua.
const CONFIG={area:20000,lote:200,onda:90,norte:{on:false,w:6},sur:0,seq:"8,4,2",gap:4,sobraAgro:true,
  franjas:[{t:"lotes",w:34,flex:true,h:2},{t:"calle",w:6,a:4,m:false},{t:"lotes",w:34,flex:true,h:2}],
  cruces:[{t:"energia",y:132,w:10,alc:"todo"}]};

// Tablaje completo en el mismo sistema (para el plano general)
const TABLAJE=[[0,0],[0,268.306107],[184.852186,304.686824],[275.080424,322.443762],[275.080831,81.809663]];

function calc(S){
  const errs=[], warns=[];
  const area=Math.min(40000,Math.max(5000,+S.area||20000));
  const k=(SS-SN)/2, X1=(YN0-Math.sqrt(YN0*YN0-4*k*area))/(2*k);
  const YS1=SS*X1, YN1=YN0+SN*X1;
  const G={X1,YS1,YN1,area,este:YN1-YS1,sur:X1*Math.hypot(1,SS),norte:X1*Math.hypot(1,SN)};
  const n=S.franjas.length;
  const LOT=Math.max(50,+S.lote||200);
  const fixed=S.franjas.reduce((s,f)=>s+(f.flex?0:Math.max(0,+f.w||0)),0);
  const nFlex=S.franjas.filter(f=>f.flex).length;
  if(fixed>X1+0.005) errs.push(`Las franjas fijas suman ${fmt(fixed,2)} m y la etapa mide ${fmt(X1,2)} m de ancho. Quita ${fmt(fixed-X1,2)} m.`);
  const flexW=nFlex?Math.max(0,(X1-fixed)/nFlex):0;
  const W=S.franjas.map(f=>f.flex?flexW:Math.max(0,+f.w||0));
  const B=[0]; W.forEach(w=>B.push(B[B.length-1]+w));
  const lam=Math.max(20,+S.onda||90);
  const off=S.franjas.map((f,i)=>{
    const a=+f.a||0; if(f.t!=="calle"||a<=0||n===1) return null;
    const ph=f.m?Math.PI:0, kk=2*Math.PI/lam;
    if(i===0) return y=>a*(1+Math.sin(kk*y+ph))/2;
    if(i===n-1) return y=>-a*(1+Math.sin(kk*y+ph))/2;
    return y=>a*Math.sin(kk*y+ph);
  });
  const bo=j=>(off[j-1]||off[j]||null);
  const nS=S.norte&&S.norte.on?Math.max(0,+S.norte.w||0)/COSN:0;
  const sS=Math.max(0,+S.sur||0)/COSS;
  const lo=y=>Math.max(0,(y-(YN0-nS))/SN);
  const hi=y=>Math.min(X1,(y-sS)/SS);

  const pieces=[];
  S.franjas.forEach((f,i)=>{
    let L,R;
    if(i===0) L=off[0]?off[0]:()=>0;
    else {const o=bo(i), b=B[i]; L=o?(y=>b+o(y)):(()=>b);}
    if(i===n-1){const b=B[n]; R=off[i]?(y=>b+off[i](y)):(()=>b);}
    else {const o=bo(i+1), b=B[i+1]; R=o?(y=>b+o(y)):(()=>b);}
    const nb=[S.franjas[i-1],S.franjas[i+1]];
    const frente=(nb[0]&&(nb[0].t==="calle"||nb[0].t==="andador"))?"izq":((nb[1]&&(nb[1].t==="calle"||nb[1].t==="andador"))?"der":"izq");
    pieces.push({t:f.t,i,L,R,w:W[i],h:f.t==="lotes"&&+f.h===2?2:1,frente});
  });
  if(off[0]) pieces.push({t:"agro",i:-1,L:()=>0,R:off[0]});
  if(n>1&&off[n-1]){const b=B[n]; pieces.push({t:"agro",i:n,L:y=>b+off[n-1](y),R:()=>b});}
  if(B[n]<X1-0.005) pieces.push({t:"agro",i:n+1,L:()=>B[n],R:()=>X1});

  const calles=S.franjas.map((f,i)=>f.t==="calle"?i:-1).filter(i=>i>=0);
  const fc=calles.length?calles[0]:-1, lc=calles.length?calles[calles.length-1]:-1;
  const crosses=(S.cruces||[]).map(c=>({t:c.t,y:+c.y,w:Math.max(0,+c.w||0),alc:c.alc,a:+c.y-(+c.w||0)/2,b:+c.y+(+c.w||0)/2}));
  const applies=(c,p)=>{ if(p.t==="calle") return false; if(c.alc==="todo"||calles.length<2) return true; return p.i>fc&&p.i<lc; };
  const PRI={calle:5,andador:4,energia:3,parque:2,agro:1};
  const crossAt=(p,y)=>{let best=null; for(const c of crosses){ if(y>=c.a&&y<c.b&&applies(c,p)&&(!best||PRI[c.t]>PRI[best.t])) best=c;} return best;};
  crosses.forEach(c=>{ if(c.b<0||c.a>YN1) warns.push({k:"av",t:`Un bloque transversal queda fuera de la etapa (posición ${fmt(c.y,1)} m).`}); });

  const bps=[]; B.concat([X1]).forEach(b=>{bps.push(SS*b+sS); bps.push(YN0-nS+SN*b);});
  const width=(p,y)=>Math.max(0,Math.min(p.R(y),hi(y))-Math.max(p.L(y),lo(y)));
  function shape(p,a,b,step){
    const ys=[a,b];
    for(let y=Math.ceil(a/step)*step;y<b;y+=step) ys.push(y);
    bps.forEach(y=>{if(y>a&&y<b) ys.push(y);});
    ys.sort((u,v)=>u-v);
    const Lp=[],Rp=[]; let y0=null,y1=null;
    for(const y of ys){
      const l=Math.max(p.L(y),lo(y)); let r=Math.min(p.R(y),hi(y));
      if(r>=l-1e-6){ r=Math.max(r,l); Lp.push([l,y]); Rp.push([r,y]); if(r-l>1e-3){ if(y0===null) y0=y; y1=y; } }
    }
    return {pts:Rp.concat(Lp.reverse()),y0,y1};
  }
  const DY=0.02;
  function integ(p,a,b,dy){ dy=dy||DY; const kk=Math.max(1,Math.ceil((b-a)/dy)), h=(b-a)/kk; let s=0; for(let j=0;j<kk;j++) s+=width(p,a+(j+.5)*h); return s*h; }
  const sub=(p,s,lado)=>lado==="izq"?{L:p.L,R:y=>Math.min(p.R(y),s)}:{L:y=>Math.max(p.L(y),s),R:p.R};

  const seq=parseSeq(S.seq);
  let ci=0;
  const acc={lotes:0,calle:0,andador:0,parque:0,agro:0,energia:0,resto:0};
  const runs=[], restos=[], slicesAll=[];
  for(const p of pieces){
    let cuts=[0,YN1];
    crosses.forEach(c=>{ if(applies(c,p)){ if(c.a>0&&c.a<YN1) cuts.push(c.a); if(c.b>0&&c.b<YN1) cuts.push(c.b);} });
    cuts=[...new Set(cuts.map(v=>+v.toFixed(6)))].sort((u,v)=>u-v);
    for(let q=0;q<cuts.length-1;q++){
      const a=cuts[q], b=cuts[q+1]; if(b-a<1e-6) continue;
      const cr=crossAt(p,(a+b)/2); const cat=cr?cr.t:p.t;
      if(cat!=="lotes"){ const ar=integ(p,a,b); if(ar>0.01){acc[cat]+=ar; runs.push({cat,p,a,b,area:ar});} continue; }
      // clusters de sur a norte, cada uno seguido de un corredor agroforestal
      const unit=LOT*p.h, gap=Math.max(0,+S.gap||0);
      const cutFrom=(y0,A)=>{ let cum=0,y=y0; while(y<b-1e-9){ const hh=Math.min(DY,b-y), dA=width(p,y+hh/2)*hh; if(cum+dA>=A&&dA>0) return y+(A-cum)/dA*hh; cum+=dA; y+=hh; } return null; };
      const needs=[...new Set(seq.map(v=>Math.max(1,Math.ceil(v/p.h))))].sort((x,z)=>z-x);
      let y=a;
      while(y<b-1e-6){
        const pref=Math.max(1,Math.ceil(seq[ci%seq.length]/p.h));
        const tryN=[pref].concat(needs.filter(x=>x<pref));
        if(!S.sobraAgro&&!tryN.includes(1)) tryN.push(1);
        let got=null;
        for(const nn of tryN){ const part=[]; let yy=y, ok=true; for(let q2=0;q2<nn;q2++){ const yc=cutFrom(yy,unit); if(yc===null){ok=false;break;} part.push({p,a:yy,b:yc}); yy=yc; } if(ok){ got={part,nn}; break; } }
        if(!got){ const ar=integ(p,y,b); if(ar>0.5){ restos.push({p,a:y,b,area:ar}); acc.resto+=ar; } break; }
        if(got.nn===pref) ci++;
        slicesAll.push({p,part:got.part,suelto:!needs.includes(got.nn)});
        y=got.part[got.part.length-1].b;
        if(gap>0&&y<b-1e-6){ const g2=Math.min(b,y+gap), ar=integ(p,y,g2); if(ar>0.01){ acc.agro+=ar; runs.push({cat:"agro",p,a:y,b:g2,area:ar,corredor:true}); } y=g2; }
      }
    }
  }
  // armar lotes y clusters
  slicesAll.sort((u,v)=>u.p.i-v.p.i||u.part[0].a-v.part[0].a);
  const lots=[], clusters=[];
  slicesAll.forEach(g=>{
    const p=g.p;
    const cl={id:clusters.length+1,p,a:g.part[0].a,b:g.part[g.part.length-1].b,lotes:[],suelto:g.suelto,part:g.part};
    cl.size=g.part.length*p.h; cl.area=cl.size*LOT;
    g.part.forEach(s=>{
      let partes;
      if(p.h===2){
        let lo2=Math.min(p.L(s.a),p.L(s.b),p.L((s.a+s.b)/2))-1, hi2=Math.max(p.R(s.a),p.R(s.b),p.R((s.a+s.b)/2))+1;
        for(let it=0;it<40;it++){ const mid=(lo2+hi2)/2; const ar=integ(sub(p,mid,"izq"),s.a,s.b,0.05); if(ar<LOT) lo2=mid; else hi2=mid; }
        const sp=(lo2+hi2)/2;
        const izq=sub(p,sp,"izq"), der=sub(p,sp,"der");
        partes=p.frente==="izq"?[izq,der]:[der,izq];
      } else partes=[p];
      partes.forEach((pp,ix)=>{ lots.push({pp,a:s.a,b:s.b,cl,atras:ix===1}); cl.lotes.push(lots.length-1); });
    });
    clusters.push(cl);
  });
  lots.forEach((l,kx)=>{
    l.n=kx+1; const sh=shape(l.pp,l.a,l.b,0.5); l.pts=sh.pts;
    l.frente=Math.max(0.01,(sh.y1??l.b)-(sh.y0??l.a)); l.fondo=LOT/l.frente;
    const ym=((sh.y0??l.a)+(sh.y1??l.b))/2; const lx=Math.max(l.pp.L(ym),lo(ym)), rx=Math.min(l.pp.R(ym),hi(ym));
    l.cx=(lx+rx)/2; l.cy=ym; l.ancho=rx-lx;
  });
  clusters.forEach(c=>{ const sh=shape(c.p,c.a,c.b,0.5); c.pts=sh.pts; c.frente=(sh.y1??c.b)-(sh.y0??c.a); c.fondo=c.area/Math.max(0.01,c.frente); });
  acc.lotes=lots.length*LOT;
  acc.calle+=X1*nS+X1*sS;

  // avisos
  S.franjas.forEach((f,i)=>{
    if(f.t!=="lotes") return;
    const nb=[S.franjas[i-1],S.franjas[i+1]].filter(Boolean);
    if(!nb.some(x=>x.t==="calle"||x.t==="andador")) warns.push({k:"av",t:`La franja ${i+1} de lotes no toca ninguna calle ni andador. Esos lotes no tendrían entrada.`});
    if(+f.h===2&&W[i]<20) warns.push({k:"av",t:`La franja ${i+1} tiene dos hileras en ${fmt(W[i],1)} m; cada lote quedaría de ${fmt(W[i]/2,1)} m de fondo.`});
  });
  S.franjas.forEach((f,i)=>{ if(f.t==="calle"&&W[i]<5.5) warns.push({k:"av",t:`La calle de la franja ${i+1} mide ${fmt(W[i],2)} m. Dos autos en sentido contrario necesitan al menos 5.5 a 6 m.`}); });
  if(!nFlex&&B[n]<X1-0.005) warns.push({k:"av",t:`Sobran ${fmt(X1-B[n],2)} m al oriente; quedan como agroforestal.`});
  const sueltos=clusters.filter(c=>c.suelto).reduce((s,c)=>s+c.size,0);
  if(sueltos) warns.push({k:"av",t:`${sueltos} ${sueltos===1?"lote queda":"lotes quedan"} fuera de un cluster completo (borde naranja).`});
  const comun=Math.max(0,area-acc.lotes);
  return {G,errs,warns,lots,clusters,runs,restos,acc,B,W,pieces,lo,hi,nS,sS,LOT,comun,shape,seq};
}
// ---------- geometría lista para dibujar ----------
const r2=v=>Math.round(v*100)/100;
const rp=pts=>pts.map(p=>[r2(p[0]),r2(p[1])]);
function simplifica(pts,tol){ // quita puntos casi colineales
  if(pts.length<4) return pts;
  const out=[pts[0]];
  for(let i=1;i<pts.length-1;i++){
    const a=out[out.length-1], b=pts[i], c=pts[i+1];
    const area=Math.abs((b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1]));
    if(area>tol) out.push(b);
  }
  out.push(pts[pts.length-1]);
  return out;
}

function geometria(){
  const R=calc(CONFIG);
  const {X1,YS1,YN1}=R.G;
  const g={G:R.G,acc:R.acc,comun:R.comun,LOT:R.LOT,etapa:[[0,0],[0,YN0],[X1,YN1],[X1,YS1]],
    calles:[],ejes:[],energia:[],paneles:[],aguadas:[],corredores:[],huellas:[],frutales:[],agro:[],restos:[],serv:[],clusters:[],info:[]};
  const inside=(r,x,y,m)=>{const l=Math.max(r.p.L(y),R.lo(y)), rr=Math.min(r.p.R(y),R.hi(y)); return x>l+m&&x<rr-m;};
  R.runs.forEach(r=>{
    const sh=R.shape(r.p,r.a,r.b,0.5); if(sh.pts.length<3) return;
    const pts=rp(simplifica(sh.pts,0.002));
    if(r.cat==="calle"){
      g.calles.push(pts);
      const e=[]; for(let y=r.a;y<=r.b;y+=1){const l=Math.max(r.p.L(y),R.lo(y)), rr=Math.min(r.p.R(y),R.hi(y)); if(rr-l>0.5) e.push([r2((l+rr)/2),r2(y)]);}
      g.ejes.push(e);
      if(!g.info.some(i=>i.k==="calle")){ const yi=58; g.info.push({k:"calle",x:(r.p.L(yi)+r.p.R(yi))/2,y:yi}); }
    } else if(r.cat==="energia"&&r.p.i===2){
      // del lado oriente, una aguada que guarda agua de lluvia
      g.energia.push(pts);
      const cy=(r.a+r.b)/2, l=Math.max(r.p.L(cy),R.lo(cy))+2.5, rr=Math.min(r.p.R(cy),R.hi(cy))-1.5;
      const cx=(l+rr)/2, rx=(rr-l)*0.4, ry=(r.b-r.a)*0.38;
      g.aguadas.push({c:[r2(cx),r2(cy)],rx,ry});
      g.info.push({k:"aguada",x:cx,y:cy});
    } else if(r.cat==="energia"){
      g.energia.push(pts);
      for(let y=r.a+1.5;y<r.b-2.5;y+=3.4){
        const y2=y+1.7; const l=Math.max(r.p.L(y),R.lo(y),r.p.L(y2),R.lo(y2))+1.2, rr=Math.min(r.p.R(y),R.hi(y),r.p.R(y2),R.hi(y2))-1.2;
        if(rr-l>2) g.paneles.push(rp([[l,y],[rr,y],[rr,y2],[l,y2]]));
      }
      if(!g.info.some(i=>i.k==="energia")) g.info.push({k:"energia",x:X1*0.25,y:(r.a+r.b)/2});
    } else if(r.cat==="agro"&&r.corredor){
      g.corredores.push(pts);
      const ym=(r.a+r.b)/2;
      [ym-0.75,ym+0.75].forEach(yh=>{
        const ya=yh-0.3, yb=yh+0.3;
        const l=Math.max(r.p.L(ya),R.lo(ya),r.p.L(yb),R.lo(yb)), rr=Math.min(r.p.R(ya),R.hi(ya),r.p.R(yb),R.hi(yb));
        if(rr-l>1) g.huellas.push(rp([[l,ya],[rr,ya],[rr,yb],[l,yb]]));
      });
      if(r.b-r.a>=3.8) [r.a+0.7,r.b-0.7].forEach((yy,fi)=>{ for(let x=2+(fi?1.6:0);x<X1;x+=3.2) if(inside(r,x,yy,0.8)) g.frutales.push([r2(x),r2(yy)]); });
      if(!g.info.some(i=>i.k==="corredor")&&r.p.i===0&&r.a>60){ const l=Math.max(r.p.L(ym),R.lo(ym)); g.info.push({k:"corredor",x:l+9,y:ym}); }
    } else {
      g.agro.push(pts);
    }
  });
  R.restos.forEach(r=>{ const sh=R.shape(r.p,r.a,r.b,0.5); if(sh.pts.length>2) g.restos.push(rp(simplifica(sh.pts,0.002))); });
  // la etiqueta del bosque va en el sobrante más grande que no choque con otra etiqueta
  const libre=(x,y)=>g.info.every(i=>Math.abs(i.y-y)>24||Math.abs(i.x-x)>12);
  for(const r of [...R.restos].sort((a,b)=>b.area-a.area)){ if(r.area<40) break; const ym=(r.a+r.b)/2, x=(Math.max(r.p.L(ym),R.lo(ym))+Math.min(r.p.R(ym),R.hi(ym)))/2; if(libre(x,ym)){ g.info.push({k:"agro",x,y:ym}); break; } }
  const full=R.clusters.filter(c=>!c.suelto);
  const corr=R.runs.filter(r=>r.corredor), ener=R.runs.filter(r=>r.cat==="energia");
  const toca=(lista,i,a,b)=>lista.some(q=>q.p.i===i&&(Math.abs(q.b-a)<0.05||Math.abs(q.a-b)<0.05));
  full.forEach((c,ix)=>{
    const ym=(c.a+c.b)/2;
    const mid=Math.floor(c.part.length/2);
    const lots=c.lotes.map(li=>{const l=R.lots[li];
      let acceso="calle";
      if(l.atras){ const k=c.part.findIndex(s=>Math.abs(s.a-l.a)<1e-6);
        acceso=toca(corr,c.p.i,l.a,l.b)?"camino":(c.size>=8&&(k===mid-1||k===mid))?"serv":l.a<0.05?"sur":toca(ener,c.p.i,l.a,l.b)?"energia":"camino"; }
      const pts=rp(simplifica(l.pts,0.002));
      return {n:l.n,atras:l.atras,acceso,frente:r2(l.frente),fondo:r2(l.fondo),centro:[r2(l.cx),r2(l.cy)],pts};});
    // punto de la etiqueta: sobre la línea entre la hilera del frente y la de atrás
    let lx=(c.p.L(ym)+c.p.R(ym))/2;
    if(c.p.h===2){ const fr=R.lots[c.lotes[0]]; const xs=fr.pts.map(p=>p[0]); lx=c.p.frente==="izq"?Math.max(...xs):Math.min(...xs); }
    g.clusters.push({num:ix+1,letra:String.fromCharCode(65+ix),size:c.size,area:c.area,frente:r2(c.frente),fondo:r2(c.fondo),banda:c.p.i===0?"poniente":"oriente",
      pts:rp(simplifica(c.pts,0.002)),label:[r2(lx),r2(ym)],lots});
    if(c.size>=8&&c.part.length>=2){
      const yb=c.part[Math.floor(c.part.length/2)-1].b;
      const sh=R.shape(c.p,yb-1.5,yb+1.5,0.5);
      if(sh.pts.length>2){ g.serv.push(rp(simplifica(sh.pts,0.002))); if(!g.info.some(i=>i.k==="serv")&&c.p.i>0) g.info.push({k:"serv",x:(c.p.L(yb)+c.p.R(yb))/2+4,y:yb}); }
    }
  });
  // ícono de cluster junto a un cluster de 4 del poniente
  const c4=g.clusters.find(c=>c.banda==="poniente"&&c.size===4);
  if(c4) g.info.push({k:"cluster",x:c4.label[0]-14,y:c4.label[1]});
  return g;
}

// ---------- SVG ----------
const LBL={
  es:{calle:"Calle central",corredor:"Camino verde",energia:"Energía y agua",agro:"Bosque agroforestal",serv:"Servidumbre",cluster:"Cluster",aguada:"Aguada",
      calleSur:"Calle al sur",etapa2:"Etapa 2 (proyecto privado)",etapas12:"Etapas 1 y 2",e1:"Etapa 1",e2:"Etapa 2",e1s:"La Villa Vikinga",e2s:"Proyecto privado",vendida:"vendida",casas:"Construcciones existentes",etapa3:"Etapa 3",m:"m",cl:"Cluster",lotes:"lotes",lote:"Lote",info:"más información"},
  en:{calle:"Central street",corredor:"Green lane",energia:"Power and water",agro:"Food forest",serv:"Easement",cluster:"Cluster",aguada:"Rain pond",
      calleSur:"South street",etapa2:"Phase 2 (private project)",etapas12:"Phases 1 and 2",e1:"Phase 1",e2:"Phase 2",e1s:"La Villa Vikinga",e2s:"Private project",vendida:"sold",casas:"Existing buildings",etapa3:"Phase 3",m:"m",cl:"Cluster",lotes:"lots",lote:"Lot",info:"more information"}
};
// Estilo de dibujo a mano: papel, tinta negra, tramas a línea y árboles de plumón olivo con sombra.
function rng(seed){return function(){seed|=0;seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
function pip(pt,poly){let c=false;for(let i=0,j=poly.length-1;i<poly.length;j=i++){const a=poly[i],b=poly[j];if(((a[1]>pt[1])!==(b[1]>pt[1]))&&(pt[0]<(b[0]-a[0])*(pt[1]-a[1])/(b[1]-a[1])+a[0]))c=!c;}return c;}
function blobD(q,r,R){ // contorno irregular suavizado alrededor de q (coordenadas de pantalla)
  const n=11, pts=[]; for(let i=0;i<n;i++){const a=i/n*Math.PI*2, rr=r*(0.74+R()*0.42); pts.push([q[0]+Math.cos(a)*rr,q[1]+Math.sin(a)*rr]);}
  const mid=(a,b)=>[(a[0]+b[0])/2,(a[1]+b[1])/2], f=v=>v.toFixed(2);
  let d=`M${f(mid(pts[n-1],pts[0])[0])},${f(mid(pts[n-1],pts[0])[1])}`;
  for(let i=0;i<n;i++){const m=mid(pts[i],pts[(i+1)%n]); d+=`Q${f(pts[i][0])},${f(pts[i][1])} ${f(m[0])},${f(m[1])}`;}
  return d+"Z";
}
// especies con su color de plumón; los pesos dan la mezcla del monte
const ESPECIES=[["claro",34],["medio",24],["oscuro",12],["oro",8],["maculis",12],["flamboyan",6],["olivo",4]];
const PESO=ESPECIES.reduce((a,e)=>a+e[1],0);
function especie(R){ let x=R()*PESO; for(const [k,w] of ESPECIES){ if((x-=w)<0) return k; } return "claro"; }
function arbol(q,r,R,sh,sp){
  const f=v=>v.toFixed(2), som=`<circle class="b-som" cx="${f(q[0]+sh)}" cy="${f(q[1]+sh)}" r="${f(r*.86)}"/>`;
  if(sp==="oscuro"||sp==="oro"){ // copa vista desde arriba con ramas radiales
    let d=""; const n=9; for(let i=0;i<n;i++){const a=i/n*Math.PI*2+R()*.3; d+=`M${f(q[0])},${f(q[1])}L${f(q[0]+Math.cos(a)*r*.82)},${f(q[1]+Math.sin(a)*r*.82)}`;}
    return som+`<circle class="t-${sp}" cx="${f(q[0])}" cy="${f(q[1])}" r="${f(r*.86)}"/><path class="t-ramas" d="${d}"/>`;
  }
  if(sp==="maculis"){ // racimo de flores rosas
    let o=som; const n=4+Math.floor(R()*3);
    for(let i=0;i<n;i++){const a=i/n*Math.PI*2+R(), d=r*.42; o+=`<circle class="t-maculis" cx="${f(q[0]+Math.cos(a)*d)}" cy="${f(q[1]+Math.sin(a)*d)}" r="${f(r*.38)}"/>`;}
    return o;
  }
  return `<path class="b-som" d="${blobD([q[0]+sh,q[1]+sh],r,rng(Math.floor(q[0]*91+q[1]*37)))}"/><path class="t-${sp}" d="${blobD(q,r,rng(Math.floor(q[0]*91+q[1]*37)))}"/>`;
}
function aguada(a,M,R,id){ // cuerpo de agua: contorno irregular, piedras en la orilla y destellos
  const n=16, pts=[];
  for(let i=0;i<n;i++){const t=i/n*Math.PI*2, k=0.82+R()*0.3; pts.push([a.c[0]+Math.cos(t)*a.rx*k,a.c[1]+Math.sin(t)*a.ry*k]);}
  const q=pts.map(p=>M(p[0],p[1])), f=v=>v.toFixed(2), mid=(u,v)=>[(u[0]+v[0])/2,(u[1]+v[1])/2];
  let d=`M${f(mid(q[n-1],q[0])[0])},${f(mid(q[n-1],q[0])[1])}`;
  for(let i=0;i<n;i++){const m=mid(q[i],q[(i+1)%n]); d+=`Q${f(q[i][0])},${f(q[i][1])} ${f(m[0])},${f(m[1])}`;}
  const c=M(a.c[0],a.c[1]); let o=`<path class="b-agua" fill="url(#agua-${id})" d="${d}"/>`;
  for(let i=0;i<18;i++){ const t=R()*Math.PI*2, k=.6+R()*.3; const p=M(a.c[0]+Math.cos(t)*a.rx*k,a.c[1]+Math.sin(t)*a.ry*k); o+=`<circle class="b-brillo" cx="${f(p[0])}" cy="${f(p[1])}" r="${f(.15+R()*.2)}"/>`; }
  pts.forEach((p,i)=>{ if(i%2) return; const t=i/n*Math.PI*2; const s=M(p[0]+Math.cos(t)*.9,p[1]+Math.sin(t)*.9); o+=`<ellipse class="b-piedra" cx="${f(s[0])}" cy="${f(s[1])}" rx="${f(.6+R()*.4)}" ry="${f(.45+R()*.3)}"/>`; });
  return o;
}
function chapo(q,R,id){ // chapoteadero en el cruce de los lotes del cluster; sirve de botón
  const f=v=>v.toFixed(2); let o="";
  for(let i=0;i<7;i++){ const t=i/7*Math.PI*2+R()*.4, d=3.25+R()*.3; o+=`<ellipse class="b-piedra" cx="${f(q[0]+Math.cos(t)*d)}" cy="${f(q[1]+Math.sin(t)*d)}" rx="${f(.55+R()*.3)}" ry="${f(.42+R()*.2)}"/>`; }
  o+=`<path class="b-chapo" fill="url(#agua-${id})" d="${blobD(q,3,R)}"/>`;
  for(let i=0;i<5;i++){ const t=R()*Math.PI*2, d=1.6+R()*.9; o+=`<circle class="b-brillo" cx="${f(q[0]+Math.cos(t)*d)}" cy="${f(q[1]+Math.sin(t)*d)}" r="${f(.12+R()*.12)}"/>`; }
  return o;
}
function arboles(poly,M,R,o){ // árboles dentro de un polígono (coordenadas locales)
  const xs=poly.map(p=>p[0]), ys=poly.map(p=>p[1]), out=[];
  const sp=o.sp||4.2, rmin=o.rmin||1.5, rmax=o.rmax||2.6, sh=o.sh||0.9;
  for(let y=Math.min(...ys)+sp/2;y<Math.max(...ys);y+=sp*0.86){
    for(let x=Math.min(...xs)+sp/2+((Math.round(y/sp)%2)?sp/2:0);x<Math.max(...xs);x+=sp){
      const px=x+(R()-.5)*sp*.5, py=y+(R()-.5)*sp*.5, r=rmin+R()*(rmax-rmin);
      const m=Math.min(r*.6,1.2); if(![[px,py],[px+m,py],[px-m,py],[px,py+m],[px,py-m]].every(p=>pip(p,poly))) continue;
      out.push(arbol(M(px,py),r,R,sh,especie(R)));
    }
  }
  return out.join("");
}
function defs(id,esc){ // tramas y filtro de tinta; esc ajusta al tamaño del plano
  return `<defs>`+
  `<pattern id="tr-calle-${id}" width="${.9*esc}" height="${.9*esc}" patternUnits="userSpaceOnUse" patternTransform="rotate(62)"><line class="b-tl" x1="0" y1="0" x2="0" y2="${.9*esc}" stroke-width="${.09*esc}"/></pattern>`+
  `<pattern id="tr-densa-${id}" width="${.4*esc}" height="${.4*esc}" patternUnits="userSpaceOnUse" patternTransform="rotate(90)"><line class="b-tl" x1="0" y1="0" x2="0" y2="${.4*esc}" stroke-width="${.08*esc}"/></pattern>`+
  `<pattern id="tr-panel-${id}" width="${.42*esc}" height="${.42*esc}" patternUnits="userSpaceOnUse"><line class="b-tl" x1="0" y1="0" x2="0" y2="${.42*esc}" stroke-width="${.07*esc}"/></pattern>`+
  `<pattern id="tr-vend-${id}" width="${2.2*esc}" height="${2.2*esc}" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line class="b-tl b-tl-suave" x1="0" y1="0" x2="0" y2="${2.2*esc}" stroke-width="${.12*esc}"/></pattern>`+
  `<radialGradient id="agua-${id}" cx="50%" cy="50%" r="55%"><stop offset="0" stop-color="#5E8FD6"/><stop offset=".65" stop-color="#93BCEB"/><stop offset="1" stop-color="#D3E6F7"/></radialGradient>`+
  `<filter id="tinta-${id}" x="-2%" y="-2%" width="104%" height="104%"><feTurbulence type="fractalNoise" baseFrequency="${(.32/esc).toFixed(3)}" numOctaves="2" seed="7"/><feDisplacementMap in="SourceGraphic" scale="${(.55*esc).toFixed(2)}"/></filter>`+
  `</defs>`;
}
function svgCapas(g,M,o){
  const P=p=>{const q=M(p[0],p[1]); return q[0].toFixed(2)+","+q[1].toFixed(2);};
  const path=pts=>"M"+pts.map(P).join("L")+"Z";
  const id=o.id, sh=o.sombra, R=rng(o.det?11:23), out=[];
  out.push(`<path class="b-base" d="${path(g.etapa)}"/>`);
  // vegetación: bosque agroforestal en los sobrantes y frutales en los caminos verdes
  g.restos.concat(g.agro).concat(g.corredores).forEach(pp=>out.push(`<path class="b-pasto" d="${path(pp)}"/>`));
  g.restos.concat(g.agro).forEach(pp=>out.push(arboles(pp,M,R,o.det?{sp:4.2,rmin:1.5,rmax:2.6,sh}:{sp:6,rmin:2.2,rmax:3.4,sh})));
  g.energia.forEach(pp=>out.push(`<path class="b-pasto" d="${path(pp)}"/>`));
  g.aguadas.forEach(a=>out.push(aguada(a,M,rng(41),id)));
  g.huellas.forEach(pp=>out.push(`<path class="b-huella" fill="url(#tr-densa-${id})" d="${path(pp)}"/>`));
  if(o.det){ const RF=rng(77); g.frutales.forEach(p=>{const q=M(p[0],p[1]), x=RF(), cls=x<.18?"t-maculis":x<.3?"t-flamboyan":x<.42?"t-oro":"b-fruta"; out.push(`<circle class="b-som" cx="${(q[0]+sh*.6).toFixed(2)}" cy="${(q[1]+sh*.6).toFixed(2)}" r=".72"/><circle class="${cls}" cx="${q[0].toFixed(2)}" cy="${q[1].toFixed(2)}" r=".72"/>`);}); }
  g.paneles.forEach(pp=>{ const q=pp.map(p=>M(p[0],p[1])); const d="M"+q.map(v=>(v[0]+sh*.8).toFixed(2)+","+(v[1]+sh*.8).toFixed(2)).join("L")+"Z"; out.push(`<path class="b-som" d="${d}"/><path class="b-panel" fill="url(#tr-panel-${id})" d="${path(pp)}"/>`); });
  // tinta: calles, lotes y contorno con trazo de mano
  const tinta=[];
  g.calles.forEach(pp=>tinta.push(`<path class="b-calle" fill="url(#tr-calle-${id})" d="${path(pp)}"/>`));
  g.corredores.forEach(pp=>tinta.push(`<path class="b-corr" d="${path(pp)}"/>`));
  g.energia.forEach(pp=>tinta.push(`<path class="b-energia" d="${path(pp)}"/>`));
  g.clusters.forEach(c=>{
    const lots=c.lots.map(l=>o.det?`<path class="b-lote lt" data-l="${l.n}" tabindex="0" role="button" aria-label="${o.L.lote} ${l.n}" d="${path(l.pts)}"/>`:`<path class="b-lote lt" data-l="${l.n}" d="${path(l.pts)}"/>`).join("");
    tinta.push(`<g class="cl" data-cl="${c.num}">${lots}<path class="b-clb" d="${path(c.pts)}"/></g>`);
  });
  g.serv.forEach(pp=>tinta.push(`<path class="b-serv" d="${path(pp)}"/>`));
  tinta.push(`<path class="b-contorno" d="${path(g.etapa)}"/>`);
  out.push(`<g filter="url(#tinta-${id})">${tinta.join("")}</g>`);
  if(o.det){
    g.clusters.forEach(c=>c.lots.forEach(l=>{ const q=M(l.centro[0],l.centro[1]); out.push(`<text class="b-ln" x="${q[0].toFixed(2)}" y="${(q[1]+.1).toFixed(2)}">${l.n}</text>`); }));
    g.clusters.forEach(c=>{ const q=M(c.label[0],c.label[1]);
      out.push(`<g class="cl-et" data-cl="${c.num}" tabindex="0" role="button" aria-label="${o.L.cl} ${c.letra}, ${c.size} ${o.L.lotes}">${chapo(q,rng(c.num*13),id)}<text class="b-clt" x="${q[0].toFixed(2)}" y="${(q[1]+0.2).toFixed(2)}">${c.letra}</text></g>`); });
  }
  return out.join("");
}
function infoIcons(g,M,L){
  return g.info.map(i=>{
    const t=L[i.k]; const w=5+t.length*1.62; const q=M(i.x,i.y);
    return `<g class="b-info" data-info="${i.k}" tabindex="0" role="button" aria-label="${t}: ${L.info}" transform="translate(${q[0].toFixed(2)},${q[1].toFixed(2)})">`+
      `<rect class="b-info-bg" x="${(-w/2).toFixed(2)}" y="-2.3" width="${w.toFixed(2)}" height="4.6"/>`+
      `<circle class="b-info-c" cx="${(-w/2+2.3).toFixed(2)}" cy="0" r="1.5"/><text class="b-info-i" x="${(-w/2+2.3).toFixed(2)}" y=".15">i</text>`+
      `<text class="b-info-t" x="${(-w/2+4.3).toFixed(2)}" y=".2">${t}</text></g>`;
  }).join("");
}
function svgDetalle(g,lang,titulo){
  const L=LBL[lang]; const {X1,YS1,YN1}=g.G;
  // girado 90°: el norte apunta a la derecha y la etapa 2 queda abajo
  const M=(x,y)=>[y,x]; const id="d"+lang;
  const vb=[-16,-9,YN1+34,X1+29];
  const o=[];
  o.push(`<svg class="plano-e3" viewBox="${vb.join(" ")}" xmlns="http://www.w3.org/2000/svg" role="group" aria-label="${titulo}">`);
  o.push(defs(id,1));
  // monte de la etapa 2, a lo largo del lindero oriente
  const vec=[[X1,YS1],[X1,YN1],[X1+13,YN1+SN*13],[X1+13,YS1+SS*13]];
  o.push(arboles(vec,M,rng(5),{sp:4.6,rmin:1.6,rmax:2.8,sh:.9,redondos:.2}));
  o.push(svgCapas(g,M,{det:true,L,id,sombra:.9}));
  o.push(`<text class="b-rot" x="${(YN1*0.62).toFixed(1)}" y="${(X1+16).toFixed(1)}">${L.etapa2}</text>`);
  o.push(infoIcons(g,M,L));
  o.push(`<text class="b-rot" transform="translate(-8,${(X1/2).toFixed(1)}) rotate(-90)">${L.calleSur}</text>`);
  const nx=YN1+12, ny=6;
  o.push(`<g class="b-norte"><path d="M${nx+4},${ny} L${nx-1.5},${ny-2} L${nx-.3},${ny} L${nx-1.5},${ny+2}Z"/><text x="${nx+7}" y="${ny+0.3}">N</text></g>`);
  const sx=YN1-22, sy=-4.5;
  o.push(`<g class="b-escala"><line x1="${sx}" y1="${sy}" x2="${sx+20}" y2="${sy}"/><line x1="${sx}" y1="${sy-1}" x2="${sx}" y2="${sy+1}"/><line x1="${sx+10}" y1="${sy-.7}" x2="${sx+10}" y2="${sy+.7}"/><line x1="${sx+20}" y1="${sy-1}" x2="${sx+20}" y2="${sy+1}"/><text x="${sx+24}" y="${sy+.3}">20 m</text></g>`);
  o.push(`</svg>`);
  return o.join("");
}
function svgGeneral(g,lang,titulo,desc){
  const L=LBL[lang]; const {X1,YS1,YN1}=g.G; const id="g"+lang;
  const M=(x,y)=>[x,-y];
  const P=p=>{const q=M(p[0],p[1]); return q[0].toFixed(2)+","+q[1].toFixed(2);};
  // etapas 1 y 2 (5 ha); el corte entre ellas es ilustrativo, a partes iguales
  const k=(SS-SN)/2, C=(YN0-Math.sqrt(YN0*YN0-4*k*(g.G.area+25000)))/(2*k);
  const e2=[[X1,YS1],[X1,YN1],[C,YN0+SN*C],[C,SS*C]];
  const e1=[[C,SS*C],[C,YN0+SN*C]].concat(TABLAJE.slice(2));
  const casas=[[206,172,10,7],[229,190,13,9],[217,211,8,6]];
  const o=[];
  o.push(`<svg class="plano-gral" viewBox="-14 -340 306 370" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="pg-t-${lang} pg-d-${lang}"><title id="pg-t-${lang}">${titulo}</title><desc id="pg-d-${lang}">${desc}</desc>`);
  o.push(defs(id,2.2));
  o.push(`<path class="b-base" d="M${e2.map(P).join("L")}Z"/><path class="b-base" d="M${e1.map(P).join("L")}Z"/>`);
  // monte de las etapas vendidas, menos denso alrededor de las casas
  const R=rng(3);
  [e2,e1].forEach(pp=>o.push(arboles(pp,M,R,{sp:14,rmin:3.4,rmax:5.6,sh:1.8,redondos:.3})));
  casas.forEach(([x,y,w,h])=>{ const pp=[[x-w/2,y-h/2],[x+w/2,y-h/2],[x+w/2,y+h/2],[x-w/2,y+h/2]]; const q=pp.map(p=>M(p[0],p[1]));
    o.push(`<path class="b-som" d="M${q.map(v=>(v[0]+2.2).toFixed(1)+","+(v[1]+2.2).toFixed(1)).join("L")}Z"/><path class="b-casa" fill="url(#tr-panel-${id})" d="M${pp.map(P).join("L")}Z"/>`); });
  o.push(svgCapas(g,M,{det:false,L,id,sombra:1.6}));
  o.push(`<g filter="url(#tinta-${id})"><path class="b-corte" d="M${P([C,SS*C])}L${P([C,YN0+SN*C])}"/><path class="b-tablaje" d="M${TABLAJE.map(P).join("L")}Z"/></g>`);
  o.push(`<text class="b-gs" x="222" y="-150">${L.casas}</text>`);
  o.push(`<text class="b-gt" x="${((X1+C)/2).toFixed(1)}" y="-178">${L.e2}</text><text class="b-gs" x="${((X1+C)/2).toFixed(1)}" y="-166">${L.e2s}</text>`);
  o.push(`<text class="b-gt" x="${((C+275)/2).toFixed(1)}" y="-262">${L.e1}</text><text class="b-gs" x="${((C+275)/2).toFixed(1)}" y="-250">${L.e1s}</text>`);
  o.push(`<text class="b-gt b-gt-on" x="${(X1/2).toFixed(1)}" y="${-(YN1+9)}">${L.etapa3}</text>`);
  o.push(`<text class="b-gs" transform="translate(140,${(-(SS*140)+12).toFixed(1)}) rotate(${(-Math.atan(SS)*180/Math.PI).toFixed(2)})">${L.calleSur}</text>`);
  o.push(`<g class="b-norte"><path d="M2,-334 L-3,-320 L2,-323 L7,-320Z"/></g>`);
  o.push(`<g class="b-escala"><line x1="225" y1="12" x2="275" y2="12"/><line x1="225" y1="9" x2="225" y2="15"/><line x1="275" y1="9" x2="275" y2="15"/><text x="250" y="23">50 m</text></g>`);
  o.push(`</svg>`);
  return o.join("");
}

if(typeof module!=="undefined") module.exports={calc,CONFIG,geometria};
if(typeof module!=="undefined"&&require.main===module){
  const g=geometria();
  const T=JSON.parse(process.argv[2]||"{}");
  const out={datos:{G:g.G,acc:g.acc,comun:g.comun,lote:g.LOT,
    etapa:g.etapa,calles:g.calles.map(p=>p.filter((_,i)=>i%3===0)),energia:g.energia,
    clusters:g.clusters.map(c=>({num:c.num,letra:c.letra,size:c.size,area:c.area,frente:c.frente,fondo:c.fondo,banda:c.banda,pts:c.pts.filter((_,i,a)=>i%2===0||i===a.length-1),lotes:c.lots.map(l=>l.n)})),
    lotes:g.clusters.flatMap(c=>c.lots.map(l=>({n:l.n,cl:c.num,atras:l.atras,acceso:l.acceso,frente:l.frente,fondo:l.fondo,pts:l.pts.filter((_,i,a)=>i%2===0||i===a.length-1)})))}};
  ["es","en"].forEach(l=>{ const t=T[l]||{}; out[l]={detalle:svgDetalle(g,l,t.detalle||""),general:svgGeneral(g,l,t.general||"",t.general_desc||"")}; });
  process.stdout.write(JSON.stringify(out));
}
