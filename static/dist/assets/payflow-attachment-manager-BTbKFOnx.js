document.addEventListener("DOMContentLoaded",function(){const a=document.getElementById("attachments-container");if(!a)return;let l=1;const o=5;function i(){const e=a.querySelectorAll(".attachment-input-row");e.forEach(t=>{t.querySelectorAll(".add-attachment, .remove-attachment").forEach(c=>c.remove())}),e.forEach((t,s)=>{const c=t.querySelector('input[type="file"]');let n=t.querySelector(".attachment-file-label");if(n||(n=document.createElement("span"),n.className="attachment-file-label text-xs text-earth-400 ml-0 bg-white border border-earth-100 rounded-lg px-3 py-2 w-full block",c.insertAdjacentElement("afterend",n),n.addEventListener("click",function(){c.click()})),c.files&&c.files.length>0){n.textContent=c.files[0].name,n.classList.remove("text-earth-400"),n.classList.add("text-earth-700");const r=document.createElement("a");r.href="#",r.className="attachment-action-link remove-attachment",r.innerHTML='<i class="fa fa-trash"></i>Borrar',t.appendChild(r)}else n.textContent="Seleccionar archivo...",n.classList.remove("text-earth-700"),n.classList.add("text-earth-400")})}a.addEventListener("click",function(e){if(e.target.classList.contains("add-attachment")&&(e.preventDefault(),l<o)){l++;const t=document.createElement("div");t.className="attachment-input-row",t.innerHTML=`
                    <input 
                        type="file" 
                        name="attachments" 
                        class="form-input attachment-input"
                        accept=".pdf,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg,.gif"
                    >
                `,a.appendChild(t),i()}if(e.target.classList.contains("remove-attachment")){e.preventDefault();const t=e.target.parentElement;a.querySelectorAll(".attachment-input-row").length>1&&(t.remove(),l--,i())}}),a.addEventListener("change",function(e){if(e.target.type==="file"&&e.target.files&&e.target.files.length>0){if(i(),l<o){l++;const t=document.createElement("div");t.className="attachment-input-row",t.innerHTML=`
                    <input 
                        type="file" 
                        name="attachments" 
                        class="form-input attachment-input"
                        accept=".pdf,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg,.gif"
                    >
                `,a.appendChild(t),i()}}else e.target.type==="file"&&i()}),i()});
