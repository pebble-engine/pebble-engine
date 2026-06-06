import sys, json, time, urllib.request
from playwright.sync_api import sync_playwright

ROUTES = ["/","/login","/signup","/forgot","/reset","/pricing","/examples",
          "/templates","/help","/trust","/privacy","/terms","/dpa",
          "/community","/inbox","/settings","/dashboard","/no-such-page-404"]
BASE="http://localhost:3001"

def check_link(href):
    if not href or href.startswith(("#","mailto:","tel:","http://","https://","javascript:")): return None
    try:
        req=urllib.request.Request(BASE+href, method="GET", headers={"User-Agent":"qa"})
        with urllib.request.urlopen(req, timeout=8) as r: return r.status
    except urllib.error.HTTPError as e: return e.code
    except Exception: return "ERR"

def audit(pg, route, vp):
    cons=[]; perr=[]
    pg.on("console", lambda m: cons.append((m.type,m.text[:120])))
    pg.on("pageerror", lambda e: perr.append(str(e)[:140]))
    try:
        resp=pg.goto(BASE+route, wait_until="domcontentloaded", timeout=40000)
    except Exception as e:
        return {"route":route,"vp":vp,"FATAL":str(e)[:100]}
    time.sleep(2.5)
    o={"route":route,"vp":vp,"status":resp.status if resp else "?","final":pg.url.replace(BASE,"")}
    o["console_errors"]=[t for ty,t in cons if ty=="error" and "404" not in t][:5]
    o["page_errors"]=perr[:3]
    o["csp"]=[t for ty,t in cons if "security policy" in t.lower()][:3]
    o["overflow_px"]=pg.evaluate("()=>document.documentElement.scrollWidth-window.innerWidth")
    o["broken_imgs"]=pg.evaluate("()=>Array.from(document.images).filter(i=>i.complete&&i.naturalWidth===0).length")
    o["h1_count"]=pg.evaluate("()=>document.querySelectorAll('h1').length")
    # unlabeled interactive controls
    o["unlabeled_controls"]=pg.evaluate("""()=>{
      const els=[...document.querySelectorAll('button,a,input,select,textarea')].filter(e=>e.offsetParent!==null);
      const bad=els.filter(e=>{
        const name=(e.innerText||e.getAttribute('aria-label')||e.getAttribute('title')||e.getAttribute('placeholder')||e.value||'').trim();
        return !name;
      });
      return bad.slice(0,6).map(e=>e.tagName+'.'+((e.className||'').toString().slice(0,30)));
    }""")
    if vp=="mobile":
        o["tiny_tap_targets"]=pg.evaluate("""()=>[...document.querySelectorAll('button,a')].filter(e=>{const r=e.getBoundingClientRect();return e.offsetParent!==null&&r.height>0&&r.height<32&&r.width>0;}).length""")
    # collect internal links once (desktop only) for dead-link check
    if vp=="desktop":
        hrefs=pg.evaluate("()=>[...new Set([...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href')))]")
        dead=[]
        for h in hrefs[:40]:
            st=check_link(h)
            if st in (404,500,"ERR") : dead.append({"href":h,"status":st})
        o["dead_links"]=dead
    return o

out=[]
with sync_playwright() as p:
    b=p.chromium.launch(headless=True)
    for vp,(w,h) in [("desktop",(1440,900)),("mobile",(390,844))]:
        for r in ROUTES:
            pg=b.new_page(viewport={"width":w,"height":h})
            try: out.append(audit(pg,r,vp))
            except Exception as e: out.append({"route":r,"vp":vp,"ERR":str(e)[:90]})
            finally: pg.close()
    b.close()
print(json.dumps(out,indent=1))
