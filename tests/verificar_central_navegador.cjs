/* Execute com Node 22+, servidor HTTP local na 8765 e Edge headless/CDP 9237.
 * Confere abas, filtros, responsividade e downloads reais nas quatro novas pastas.
 */
const fs=require('fs'),path=require('path'),assert=require('assert');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 const targets=await(await fetch('http://127.0.0.1:9237/json/list')).json();
 const ws=new WebSocket(targets.find(t=>t.type==='page').webSocketDebuggerUrl);
 await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
 let id=0;const pending=new Map();
 ws.onmessage=e=>{const d=JSON.parse(e.data);if(d.id){const p=pending.get(d.id);pending.delete(d.id);d.error?p.reject(d.error):p.resolve(d.result);}};
 const cmd=(method,params={})=>new Promise((resolve,reject)=>{const n=++id;pending.set(n,{resolve,reject});ws.send(JSON.stringify({id:n,method,params}));});
 const evaluate=async expression=>{const r=await cmd('Runtime.evaluate',{expression,returnByValue:true,userGesture:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;};
 const destino=path.resolve('.preview-central/downloads-refinados-'+Date.now());fs.mkdirSync(destino,{recursive:true});
 await cmd('Browser.setDownloadBehavior',{behavior:'allow',downloadPath:destino});
 await cmd('Page.enable');await cmd('Page.navigate',{url:'http://127.0.0.1:8765/index.html'});
 for(let i=0;i<100;i++){if(await evaluate("document.readyState==='complete' && document.getElementById('premium-tab-1')"))break;await sleep(100);}
 assert.equal(await evaluate("document.querySelectorAll('#materiais-premium [download]').length"),41);
 for(const i of [2,3,1]){
  const visible=await evaluate(`(() => {document.getElementById('premium-tab-${i}').click();return [...document.querySelectorAll('#materiais-premium .premium-panel')].filter(p=>!p.hidden).map(p=>p.id)})()`);
  assert.deepEqual(visible,[`premium-panel-${i}`]);
 }
 assert(await evaluate("[...document.querySelectorAll('.course-tabs [role=tab]')].length === 6 || document.querySelectorAll('#minicursos [role=tab]').length === 6"));
 const busca=await evaluate(`(() => {document.getElementById('premium-tab-2').click();const input=document.getElementById('portais-br');input.closest('details').open=true;input.value='topografia';input.dispatchEvent(new Event('input'));return [...input.closest('details').querySelectorAll('[data-portal]')].filter(p=>!p.hidden).map(p=>p.querySelector('h4').textContent);})()`);
 assert.deepEqual(busca,['InfoJobs']);
 assert(await evaluate(`(() => {const input=document.getElementById('portais-br');input.value='zzzzz';input.dispatchEvent(new Event('input'));return !input.closest('details').querySelector('.portal-empty').hidden;})()`));
 for(const largura of [1440,390]){
  await cmd('Emulation.setDeviceMetricsOverride',{width:largura,height:900,deviceScaleFactor:1,mobile:largura<500});
  const excessos=await evaluate(`(() => {const root=document.getElementById('materiais-premium');document.getElementById('premium-tab-1').click();root.querySelectorAll('details').forEach(d=>d.open=true);return [...root.querySelectorAll('.refined-group,.refined-item,.premium-featured')].filter(el=>el.getClientRects().length&&el.getBoundingClientRect().right>innerWidth+1).length;})()`);
  assert.equal(excessos,0,`Overflow em ${largura}px`);
 }
 for(const [tab,pasta] of [[1,'scripts_topografia'],[1,'scripts_bancos_geo'],[3,'desafios_python'],[3,'roteiros_servidores']]){
  const file=await evaluate(`(() => {document.getElementById('premium-tab-${tab}').click();const a=document.querySelector('#materiais-premium a[href^="./${pasta}/"]');a.closest('details').open=true;a.click();return {name:a.download,href:a.getAttribute('href')};})()`);
  const esperado=path.join(destino,file.name);
  for(let n=0;n<100&&!fs.existsSync(esperado);n++)await sleep(100);
  assert(fs.existsSync(esperado),file.name);
  assert(fs.readFileSync(esperado).equals(fs.readFileSync(path.resolve(file.href))),file.name);
  console.log('Download OK:',file.name);
 }
 await cmd('Browser.close');ws.close();
 console.log('OK: abas, filtros, 1440/390px e quatro downloads reais.');
})().catch(e=>{console.error(e);process.exit(1);});
