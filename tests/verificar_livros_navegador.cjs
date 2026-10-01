/* Node 22+; HTTP localhost:8765 e navegador CDP:9237. */
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
 const dest=path.resolve('.preview-central/downloads-livros-'+Date.now());fs.mkdirSync(dest,{recursive:true});
 await cmd('Browser.setDownloadBehavior',{behavior:'allow',downloadPath:dest});
 await cmd('Page.enable');await cmd('Page.navigate',{url:'http://127.0.0.1:8765/index.html'});
 for(let n=0;n<100;n++){if(await evaluate("document.readyState==='complete' && !!document.getElementById('book-tab-1')"))break;await sleep(100);}
 const base=await evaluate("[...document.querySelectorAll('#mini-cursos [role=tab],#materiais-premium [role=tab]')].map(t=>t.getAttribute('aria-selected'))");
 for(const width of [1440,390]){
  await cmd('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:width<500});
  for(let i=1;i<=6;i++){
   const info=await evaluate(`(() => {const root=document.getElementById('livros-tecnicos');document.getElementById('book-tab-${i}').click();const panel=root.querySelector('.academic-panel:not([hidden])');return {id:panel.id,cards:panel.querySelectorAll('article').length,overflow:[...panel.querySelectorAll('.academic-card')].some(c=>c.getBoundingClientRect().right>innerWidth+1),cropped:[...panel.querySelectorAll('.academic-cover')].some(c=>c.scrollHeight>c.clientHeight+1)};})()`);
   assert.equal(info.id,`book-panel-${i}`);assert.equal(info.cards,5);assert(!info.overflow,`Overflow: ${width}, area ${i}`);assert(!info.cropped,`Capa cortada: ${width}, area ${i}`);
  }
  await evaluate("document.getElementById('book-tab-1').click();document.getElementById('livros-tecnicos').scrollIntoView({behavior:'instant'})");
  await sleep(400);
  const shot=await cmd('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
  fs.writeFileSync(path.resolve(`.preview-central/livros-${width}.png`),Buffer.from(shot.data,'base64'));
 }
 await evaluate("document.getElementById('book-tab-1').focus();document.getElementById('book-tab-1').dispatchEvent(new KeyboardEvent('keydown',{key:'End',bubbles:true}))");
 assert.equal(await evaluate("document.activeElement.id"),'book-tab-6');
 assert.deepEqual(await evaluate("[...document.querySelectorAll('#mini-cursos [role=tab],#materiais-premium [role=tab]')].map(t=>t.getAttribute('aria-selected'))"),base);
 for(let i=1;i<=6;i++)for(let j=0;j<5;j++){
  const file=await evaluate(`(() => {document.getElementById('book-tab-${i}').click();const a=document.querySelectorAll('#book-panel-${i} a[download]')[${j}];a.click();return {name:a.download,href:a.getAttribute('href')};})()`);
  const target=path.join(dest,file.name);
  for(let n=0;n<100&&!fs.existsSync(target);n++)await sleep(100);
  assert(fs.existsSync(target),file.name);
  assert(fs.readFileSync(target).equals(fs.readFileSync(path.resolve(decodeURIComponent(file.href)))),file.name);
 }
 await cmd('Browser.close');ws.close();
 console.log('OK: 6 abas, 5 cards em cada, teclado, 1440/390px, capas sem corte e 30 downloads reais.');
})().catch(e=>{console.error(e);process.exit(1);});
