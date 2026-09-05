let all=[];
const money=x=>"₹"+Number(x).toLocaleString("en-IN",{maximumFractionDigits:0});
async function load(){
 const d=await fetch("/api/dashboard").then(x=>x.json());
 document.getElementById("risk").textContent=money(d.revenue_at_risk);
 document.getElementById("rec").textContent=money(d.recovered);
 document.getElementById("rate").textContent=d.recovery_rate+"%";
 const a=await fetch("/api/analytics").then(x=>x.json());
 document.getElementById("high").textContent=a.high_risk;
 document.getElementById("analytics").innerHTML=`<p><b>Top revenue-loss cause:</b> ${a.top_reason}</p><p><b>Cases overdue >30 days:</b> ${a.overdue_30}</p><p><b>Average risk score:</b> ${a.avg_risk}%</p><p><b>Total transaction value:</b> ${money(a.total_value)}</p>`;
 all=await fetch("/api/cases").then(x=>x.json()); render();
}
function render(){
 const q=document.getElementById("search").value.toLowerCase();
 const arr=all.filter(x=>(x.customer+" "+x.reason).toLowerCase().includes(q));
 document.getElementById("rows").innerHTML=arr.map(x=>`<tr>
 <td><b>${x.customer}</b><br>${x.type}</td><td>${money(x.amount)}</td><td>${x.reason}</td>
 <td class="prob">${x.probability}%<br>${x.risk_band}</td><td>${x.diagnosis}<br><small>Guardrail: ${x.guardrail}</small></td>
 <td>${x.action}</td><td>${x.status==="paid"?"PAID":`<button onclick="executeCase('${x.id}')">Execute</button>`}</td></tr>`).join("");
}
async function executeCase(id){const r=await fetch("/api/execute/"+id,{method:"POST"}).then(x=>x.json());alert(r.message);load();}
document.getElementById("search").addEventListener("input",render);load();
