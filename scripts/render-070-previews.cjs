// Render locally generated Lua layout demonstrations, not a live WoW client.
const {chromium}=require('playwright');
const fs=require('fs');
const path=require('path');
const {pathToFileURL}=require('url');
(async()=>{
 const candidates=[process.env.FAMILIARFACES_PREVIEW_BROWSER,'C:/Program Files/Google/Chrome/Application/chrome.exe','C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'].filter(Boolean);
 const executablePath=candidates.find(p=>fs.existsSync(p));
 if(!executablePath) throw new Error('Set FAMILIARFACES_PREVIEW_BROWSER to Chromium.');
 const browser=await chromium.launch({headless:true,executablePath});
 try {
  const page=await browser.newPage({viewport:{width:1160,height:1080},deviceScaleFactor:1});
  const folder=path.resolve(__dirname,'../assets/curseforge/0.7.0');
  const narrow=path.join(folder,'description-800'); fs.mkdirSync(narrow,{recursive:true});
  for(const name of fs.readdirSync(folder).filter(n=>n.endsWith('.html'))){
   await page.goto(pathToFileURL(path.join(folder,name)).href);
   await page.evaluate(()=>Promise.all([...document.images].map(i=>i.decode())));
   await page.screenshot({path:path.join(folder,name.replace('.html','.png')),fullPage:true});
   const height=await page.evaluate(()=>document.documentElement.scrollHeight);
   await page.evaluate(()=>{document.body.style.width='1160px'; document.body.style.zoom=String(800/1160);});
   await page.screenshot({path:path.join(narrow,name.replace('.html','.png')),clip:{x:0,y:0,width:800,height:Math.ceil(height*800/1160)}});
  }
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
