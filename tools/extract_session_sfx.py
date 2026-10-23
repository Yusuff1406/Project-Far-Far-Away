#!/usr/bin/env python3
"""Render selected effects offline with the ROM's own GAX driver; Android plays WAVs."""
import argparse,hashlib,json,struct,sys,wave,array
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_INTR,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from extract import Rom

class GaxOracle:
 def __init__(self,rom,rate=15769,song=None):
  self.u=u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.ctl_set_cpu_model(UC_CPU_ARM_TI925T)
  u.mem_map(0x08000000,len(rom));u.mem_write(0x08000000,rom)
  u.mem_map(0x02000000,0x40000);u.mem_write(0x02000000,rom[0x708bdc:0x70b990])
  u.mem_map(0x03000000,0x8000);u.mem_write(0x03000000,rom[0x707dd8:0x708bdc]);u.mem_map(0x04000000,0x1000)
  self.swi_counts={}
  def bios(uc,number,ctx):
   pc=uc.reg_read(UC_ARM_REG_PC);thumb=bool(uc.reg_read(UC_ARM_REG_CPSR)&32)
   ins=bytes(uc.mem_read(pc-(2 if thumb else 4),2 if thumb else 4));swi=ins[0] if thumb else ins[2]
   self.swi_counts[swi]=self.swi_counts.get(swi,0)+1
   src,dst,control=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]
   if swi in [11,12]:
    size=4 if swi==12 or control&(1<<26) else 2;count=control&0x1fffff
    if swi==12:assert count%8==0
    block=bytes(uc.mem_read(src,size if control&(1<<24) else size*count))
    uc.mem_write(dst,block*count if control&(1<<24) else block)
   elif swi==6:
    signed=lambda x:x-2**32 if x&0x80000000 else x
    a,b=signed(src),signed(dst);assert b
    q=abs(a)//abs(b)*(-1 if (a<0)!=(b<0) else 1)
    for reg,val in [(UC_ARM_REG_R0,q),(UC_ARM_REG_R1,a-q*b),(UC_ARM_REG_R3,abs(q))]:uc.reg_write(reg,val&0xffffffff)
   else:raise AssertionError(('unsupported BIOS SWI',swi,hex(pc)))
  u.hook_add(UC_HOOK_INTR,bios)
  self.params=0x02003800;self.call(0x0801bf7c,self.params)
  u.mem_write(self.params,struct.pack('<IIHH',0x02010000,0x2c000,rate,rate))
  u.mem_write(self.params+0x10,struct.pack('<H',2));u.mem_write(self.params+0x2c,struct.pack('<I',0x081cb9bc))
  if song is not None:u.mem_write(self.params+0x30,struct.pack("<I",song))
  self.call(0x0801bd58,self.params);self.call(0x0801c45c,self.params);assert u.reg_read(UC_ARM_REG_R0)==1
  self.manager=self.word(0x02006300);self.channels=self.word(self.manager+12)
  header=self.word(self.manager+0x24);self.rate=struct.unpack('<H',u.mem_read(header+2,2))[0];self.samples=struct.unpack('<H',u.mem_read(header+4,2))[0]
  assert self.rate==rate and 0<self.samples<=1024
 def word(self,address):return struct.unpack('<I',self.u.mem_read(address,4))[0]
 def call(self,address,*args):
  u=self.u
  for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,val&0xffffffff)
  u.reg_write(UC_ARM_REG_SP,0x0203f000);u.reg_write(UC_ARM_REG_LR,0x03007f01)
  u.emu_start(address|1,0x03007f00,count=2000000);assert u.reg_read(UC_ARM_REG_PC)==0x03007f00
 def mix_precise(self):
  # Capture actual original mixer accumulator and bias before the final >>5.
  outputIndex=self.word(self.manager+0x48)
  if not hasattr(self,'precise_hook'):
   self.precise_blocks=[];self.precise_finish=self.word(self.manager+0x68)
   def persistent_capture(uc,address,size,context):
    if address!=self.precise_finish:return
    src,dst,count,bias=struct.unpack('<4I',uc.mem_read(uc.reg_read(UC_ARM_REG_R0),16));bias<<=4;values=struct.unpack('<'+'H'*count,uc.mem_read(src,count*2));self.precise_blocks.append((dst,[max(-4065,min(4064,int(x)-bias)) for x in values]))
   self.precise_hook=self.u.hook_add(UC_HOOK_CODE,persistent_capture,begin=self.precise_finish,end=self.precise_finish+4)
  self.precise_blocks.clear();self.call(0x0801cfa0);captured=self.precise_blocks
  if not captured:
   raw=bytes(self.u.mem_read(self.word(self.manager+0x30)+outputIndex*self.samples,self.samples));assert not any(raw), "Non-silent output without accumulator callback";self.call(0x0801ce80);return bytes(self.samples*2)
  assert len(captured)==1,len(captured);dst,values=captured[0];actual=bytes(self.u.mem_read(dst,len(values)));assert actual==bytes((x>>5)&255 for x in values), 'Original final quantizer differs'
  pcm=array.array('h',(x*8 for x in values))
  if sys.byteorder!='little':pcm.byteswap()
  self.call(0x0801ce80);return pcm.tobytes()
 def render(self,sound,channel=0):
  self.call(0x0801d234,sound,channel,100,-1);assert self.u.reg_read(UC_ARM_REG_R0)==channel
  self.call(0x0801da20,channel,255)
  pcm=bytearray();ended=None
  for tick in range(600):
   pcm.extend(self.mix_precise())
   if self.word(self.channels+channel*0x50+0x40)==0x80000000 and ended is None:ended=tick
   if ended is not None and tick>=ended+2:break
  assert ended is not None,('effect did not finish',sound)
  assert max(pcm)-min(pcm)>8,('silent effect',sound)
  return bytes(pcm),tick+1

def main():
 ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();rom=Rom(a.rom).data
 out=ROOT/'android/app/src/main/assets/session/audio';out.mkdir(parents=True,exist_ok=True);items=[]
 for sound in [1,5,10,31,44,45,46,54,59,60,64,65,67,68,78,79,82,86,88,90,93,94,96,100,102,103]:
  oracle=GaxOracle(rom,rate=31537);pcm,ticks=oracle.render(sound)
  # Both original effect slots produce the same isolated waveform.
  other=GaxOracle(rom,rate=31537);copy,other_ticks=other.render(sound,1);assert copy==pcm and other_ticks==ticks
  p=out/f'sfx_{sound}.wav'
  with wave.open(str(p),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(oracle.rate);w.writeframes(pcm)
  items.append({'sound_id':sound,'file':p.name,'sample_rate':oracle.rate,'samples':len(pcm)//2,'driver_ticks':ticks,'duration_seconds':len(pcm)/2/oracle.rate,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pcm_sha256':hashlib.sha256(pcm).hexdigest()})
 report={'effects':items,'rom_sha256':hashlib.sha256(rom).hexdigest(),'fx_bank':0x081cb9bc,'instrument_table':0x08056c48,'sample_table':0x081cb67c,'oracle_cpu_model':'Unicorn TI925T (ARMv4T), not a whole GBA emulator','bios_fixtures':['Div','CpuSet','CpuFastSet'],'hardware_fixture':'Memory-backed I/O; driver render buffers captured before FIFO hardware. GAX init/start/mix/IRQ execute from ROM. No BIOS timing, analog output, music, or live native GAX mixer validation.','scope':'Selected effects synthesized at31537Hz, precise original accumulator before hardware8-bit quantization, PCM16LE. Each block matches original final quantizer after >>5. Instrument source quality and GBA analog filtering remain unchanged/unmodeled.'}
 (ROOT/'docs/session_sfx_resources.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
