import os, sys, google.generativeai as genai
from omega_config import config
API="api_key.txt"; LOG="nnab_crash.log"; CORE="nnab_core.py"
def heal():
 if not os.path.exists(LOG): return
 with open(LOG,"r") as f: err=f.read()
 if not err.strip(): return
 try:
  with open(API,"r") as f: genai.configure(api_key=f.read().strip())
  m=genai.GenerativeModel(config.get('ai',{}).get('model','gemini-2.5-flash'))
  res=m.generate_content(f"Fix Python code based on error:\nERR:\n{err}\nCODE:\n{open(CORE).read()}\nOUT:Raw code only")
  fix=res.text.replace("```python","").replace("```","").strip()
  if len(fix)>50: 
   with open(CORE,"w") as f: f.write(fix)
   print("REPAIRED.")
 except: pass
if __name__=="__main__": heal()
