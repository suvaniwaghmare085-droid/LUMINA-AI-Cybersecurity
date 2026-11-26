const API = "http://127.0.0.1:5000/api";
const content = document.getElementById("content");
const result = document.getElementById("result");
function safe(s){return String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
async function analyze(value, type="auto"){
  if(!value.trim()){result.textContent="No content found. Select text or paste a message/URL.";return;}
  result.textContent="Analyzing…";
  try{
    const r=await fetch(`${API}/analyze`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({input:value,type})});
    const d=await r.json();if(!r.ok)throw new Error(d.error||"Analysis failed");
    result.innerHTML=`<b>${safe(d.risk_level)} · ${d.risk_score}/100</b><br>${d.reasons.map(safe).join("<br>")}<br><br><small>${safe(d.disclaimer)}</small>`;
  }catch(e){result.textContent=e.message.includes("Failed to fetch")?"Backend unavailable. Start the LUMINA Flask server first.":e.message;}
}
document.getElementById("analyze").addEventListener("click",()=>analyze(content.value));
document.getElementById("selected").addEventListener("click",async()=>{
  try{const [tab]=await chrome.tabs.query({active:true,currentWindow:true});const [{result:text}]=await chrome.scripting.executeScript({target:{tabId:tab.id},func:()=>window.getSelection().toString()});content.value=text||"";analyze(content.value,"text");}catch(e){result.textContent="This page does not allow text selection access. Copy and paste the text instead.";}
});
document.getElementById("page").addEventListener("click",async()=>{
  try{const [tab]=await chrome.tabs.query({active:true,currentWindow:true});content.value=tab.url||"";analyze(content.value,"url");}catch(e){result.textContent="Unable to read this tab address. Paste the URL instead.";}
});
