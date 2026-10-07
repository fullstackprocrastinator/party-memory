"""Export the real Familiar Faces Lua layout with mock data for visual QA."""
from pathlib import Path
import sys, html, re
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests'))
from test_addon import AddonTests
DEST=ROOT/'docs'/'previews'/'familiar-faces'
RECORD=r'''
local original=CreateFrame
local id=0
function CreateFrame(kind,name,parent,template)
 local f=original(kind,name,parent,template); id=id+1
 f.previewId=id; f.parent=parent; f.width=0; f.height=0
 f.SetPoint=function(self,p,a,b,c,d) if not self.anchor then self.anchor=p; self.x=type(a)=='number' and a or c or 0; self.y=-(type(b)=='number' and b or d or 0) end end
 f.ClearAllPoints=function(self) self.anchor=nil end
 f.SetHeight=function(self,h) self.height=h end
 f.SetFrameStrata=function(self,s) self.strata=s end
 f.SetAllPoints=function(self) self.allPoints=true end
 f.SetTexture=function(self,p) self.texture=p end
 f.SetVertexColor=function(self,r,g,b,a) self.color={r,g,b,a or 1} end
 f.SetTextColor=function(self,r,g,b,a) self.textColor={r,g,b,a or 1} end
 f.SetJustifyH=function(self,a) self.align=a end
 f.CreateTexture=function(self,n,l) local t=CreateFrame('Texture',n,self); t.layer=l; return t end
 f.CreateFontString=function(self,n,l,font) local t=CreateFrame('FontString',n,self); t.font=font; return t end
 return f
end
'''
def color(c,default):
 return default if c is None else 'rgba(%d,%d,%d,%s)'%(round(c[1]*255),round(c[2]*255),round(c[3]*255),c[4])
def text(s):
 s=html.escape(str(s or '')); s=re.sub(r'\|cff([a-fA-F0-9]{6})',r'<span style="color:#\1">',s)
 return s.replace('|r','</span>').replace('\n','<br>')
def render(state):
 test=AddonTests(); test.setUp(); lua=test.lua; lua.execute(RECORD)
 if state!='empty':
  lua.execute('''
   roster={{name='Alice',realm='HomeRealm',class='PRIEST',role='HEALER'},
    {name='Bram',realm='HomeRealm',class='WARRIOR',role='TANK'},
    {name='Elowen',realm='HomeRealm',class='PRIEST',role='DAMAGER'}}
   clock=1791126000; FamiliarFaces.Capture()
   clock=clock+600; zone='Deadmines'; instanceType='party'; FamiliarFaces.Capture()
   clock=clock+1800; FamiliarFaces.Capture(); FamiliarFaces.EndSession(clock)
   FamiliarFaces.db.people['Alice-HomeRealm'].note='Patient healer. Great company.'
   FamiliarFaces.db.people['Alice-HomeRealm'].favourite=true
  ''')
 lua.execute("SlashCmdList.FAMILIARFACES('')")
 if state=='adventures': lua.execute("for _,b in ipairs(buttons) do if b.entry then b.scripts.OnClick(b); break end end")
 if state=='companions': lua.execute("clickText('Companions'); for _,b in ipairs(buttons) do if b.entry and b.entry.name=='Alice-HomeRealm' then b.scripts.OnClick(b); break end end")
 frames={int(f['previewId']):f for f in lua.globals().frames.values() if f['previewId']}
 children={}
 for key,f in frames.items():
  p=f['parent']; children.setdefault(int(p['previewId']) if p and p['previewId'] else 0,[]).append(key)
 def element(key):
  f=frames[key]
  if not f['visible']: return ''
  p=f['parent']; w=float(f['width'] or 0); h=float(f['height'] or 0)
  pw=float(p['width'] or 0) if p and p['previewId'] else 1120; ph=float(p['height'] or 0) if p and p['previewId'] else 880
  if f['kind']=='Texture' and 'WHITE8X8' in (f['texture'] or ''):
   if h==1 and not w: w=pw
   if w==1 and not h: h=ph
  if f['allPoints']: w=pw; h=ph
  x=float(f['x'] or 0); y=float(f['y'] or 0); anchor=f['anchor'] or 'TOPLEFT'
  if 'RIGHT' in anchor: x+=pw-w
  if 'BOTTOM' in anchor: y+=ph-h
  if anchor=='CENTER': x+=(pw-w)/2; y+=(ph-h)/2
  css=[f'left:{x}px',f'top:{y}px']
  if f['strata']=='FULLSCREEN_DIALOG': css.append('z-index:50')
  if w: css.append(f'width:{w}px')
  if h: css.append(f'height:{h}px')
  body=''; kind=f['kind']
  if kind=='Texture':
   css.append('z-index:'+('0' if f['layer']=='BACKGROUND' else '1'))
   path=f['texture'] or ''
   if 'WHITE8X8' in path: css.append('background:'+color(f['color'],'#a88642'))
   elif path.endswith('.tga'): body='<img src="Wordmark.png" style="width:100%;height:100%">'
   elif '\\Icons\\' in path:
    css.extend(['background:#24444a','border:1px solid #af8444']); body='<span style="display:block;text-align:center;color:#f1c370;font-size:18px">◇</span>'
  elif kind=='FontString':
   size=18 if f['font']=='GameFontNormalLarge' else (14 if f['font']=='GameFontNormal' else 12)
   css.extend(['z-index:3',f'font-size:{size}px',f'line-height:{size+3}px','overflow:hidden','white-space:nowrap','color:'+color(f['textColor'],'#f1c370' if 'Normal' in (f['font'] or '') else '#f4ebd8')]); body=text(f['text'])
  elif kind=='EditBox':
   css.extend(['border:1px solid #6b777e','background:#071820','padding:5px','color:#f4ebd8']); body=text(f['text'])
  if kind!='Texture': body+=''.join(element(k) for k in children.get(key,[]))
  return '<div class="region" style="'+';'.join(css)+'">'+body+'</div>'
 page='<!doctype html><meta charset="utf-8"><title>Familiar Faces layout preview</title><style>body{margin:0;background:#172935;font:12px Arial;color:#eee}.region{position:absolute;box-sizing:border-box}.window{position:relative;width:1120px;height:880px;margin:20px}img{display:block}</style><p style="margin:20px">Familiar Faces · Lua layout preview · Sample data · Native icons and input skins are placeholders</p><div class="window">'+''.join(element(k) for k in children.get(0,[]))+'</div>'
 (DEST/(state+'.html')).write_text(page,encoding='utf-8')
DEST.mkdir(parents=True,exist_ok=True)
Image.open(ROOT/'FamiliarFaces'/'Textures'/'Wordmark.tga').save(DEST/'Wordmark.png')
for state in ('empty','adventures','companions'): render(state)
print(DEST)
