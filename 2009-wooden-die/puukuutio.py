#!/usr/bin/python

from sets import Set
import sys
import pygame
import time
from OpenGL.GL import *
from OpenGL.GLU import *

POHJA,KATTO,YLA,ALA,VAS,OIK = range(6)
TYHJA,PUN,VIHR,EIMIK = range(4)

# Kommenteissa huijausparametrit
MAXRATKAISUT = 10000 #940
MINHAKU = 0 #890

class Osa:
	def __init__(self,nro):
		self.osat = [TYHJA]*6
		self.nro = nro

	def kaannetty1(self):
		uusi = Osa(self.nro);
		uusi.osat[VAS] = self.osat[VAS]
		uusi.osat[OIK] = self.osat[OIK]
		uusi.osat[KATTO] = self.osat[YLA]
		uusi.osat[YLA] = self.osat[POHJA]
		uusi.osat[POHJA] = self.osat[ALA]
		uusi.osat[ALA] = self.osat[KATTO]
		return uusi

	def kaannetty2(self):
		uusi = Osa(self.nro);
		uusi.osat[POHJA] = self.osat[POHJA]
		uusi.osat[KATTO] = self.osat[KATTO]
		uusi.osat[YLA] = self.osat[VAS]
		uusi.osat[VAS] = self.osat[ALA]
		uusi.osat[ALA] = self.osat[OIK]
		uusi.osat[OIK] = self.osat[YLA]
		return uusi

	def kopio(self):
		uusi = Osa(self.nro);
		uusi.osat = self.osat[:]
		return uusi

class Pala:
	#
	#	12
	#	3
	#
	def __init__(self,nro):
		self.nro = nro
		self.osat = [Osa(nro),Osa(nro),Osa(nro)]
		self.paikat = [(0,0,0),(1,0,0),(0,0,-1)]

	def kaannetty1(self):
		uusi = Pala(self.nro)
		for i in range(3):
			uusi.osat[i] = self.osat[i].kaannetty1();
			uusi.paikat[i] = ( self.paikat[i][0], -self.paikat[i][2], self.paikat[i][1] )
		return uusi

	def kaannetty2(self):
		uusi = Pala(self.nro)
		for i in range(3):
			uusi.osat[i] = self.osat[i].kaannetty2();
			uusi.paikat[i] = ( self.paikat[i][1], -self.paikat[i][0], self.paikat[i][2] )
		return uusi
			
	def siirretty(self,p):
		uusi = Pala(self.nro)
		uusi.osat = [ self.osat[i].kopio() for i in range(3) ]
		uusi.paikat = [ vecsum(self.paikat[i],p) for i in range(3) ]
		return uusi
		
	def taso(self):
		return min([self.paikat[i][2] for i in range(3)])

def vecsum(v1,v2):
	return ( v1[0]+v2[0], v1[1]+v2[1], v1[2]+v2[2] )

class Kuutio:
	def __init__(self):
		self.paikat = [False]*(3*3*3)

	def kopio(self):
		uusi = Kuutio()
		uusi.paikat = self.paikat[:]
		return uusi

	def sopiiko_pala(self,pala):
		for i in range(3):
			if not self.vapaa_paikka(pala.paikat[i]): return False
		return True

	def aseta_pala(self,pala):
		for i in range(3):
			self.aseta_osa(pala.osat[i],pala.paikat[i])

	def paikka(self,p):
		return p[0]*3*3 + p[1]*3 + p[2]

	def kaannetty1(self):
		uusi = Kuutio()
		for x in range(3):
		 for y in range(3):
		  for z in range(3):
			ux = x
			uy = -(z-1)+1
			uz = y
			uusi_osa = False
			vanha_osa = self.paikat[self.paikka((x,y,z))]
			if vanha_osa != False:
				uusi_osa = vanha_osa.kaannetty1()
			uusi.paikat[uusi.paikka((ux,uy,uz))] = uusi_osa
		return uusi

	def kaannetty2(self):
		uusi = Kuutio()
		for x in range(3):
		 for y in range(3):
		  for z in range(3):
			ux = y
			uy = -(x-1)+1
			uz = z
			vanha_osa = self.paikat[self.paikka((x,y,z))]
			uusi_osa = False
			if vanha_osa != False:
				uusi_osa = vanha_osa.kaannetty2()
			uusi.paikat[self.paikka((ux,uy,uz))] = uusi_osa
		return uusi

	def validi(self,p):
		if p[0] < 0 or p[0] >= 3: return False
		if p[1] < 0 or p[1] >= 3: return False
		if p[2] < 0 or p[2] >= 3: return False
		return True

	def vapaa_paikka(self,p):
		if not self.validi(p): return False
		if self.paikat[self.paikka(p)] != False: return False
		return True

	def aseta_osa(self,osa,p):
		self.paikat[self.paikka(p)] = osa.kopio()
		
	def rakenna_sivu(self,mika):
		sivu = [TYHJA]*9
		for i in range(3):
			for j in range(3):
				p = (0,0,0)
				if mika==POHJA: p = (i,j,0)
				elif mika==KATTO: p = (i,j,2)
				elif mika==YLA: p = (i,2,j)
				elif mika==ALA: p = (i,0,j)
				elif mika==VAS: p = (0,i,j)
				elif mika==OIK: p = (2,i,j)
				osa = self.paikat[self.paikka(p)]
				t = EIMIK
				if osa != False: t = osa.osat[mika]
				sivu[i*3+j] = t
		return sivu

	def tunnista(self,mika):
		sivu = self.rakenna_sivu(mika)
		loyt = [0,0,0,0]
		for t in sivu: loyt[t] += 1
			
		if loyt[PUN]>0 and loyt[VIHR]>0: return (-1,EIMIK)
		l = PUN	
		if loyt[l]==0: l = VIHR
		n = loyt[l]
		if n == 0: l = EIMIK

		if n>6: return (-1,l)
		
		if mika==POHJA:
			if n+loyt[EIMIK]<6: return (-1,l)
			n = 6
		elif mika==KATTO:
			if n>1: return (-1,l)
			n = 1
		elif mika==OIK:
			if n>2 or n+loyt[EIMIK]<2: return (-1,l)
			n = 2
		elif mika==VAS:
			if n+loyt[EIMIK]<5 or n>5: return (-1,l)
			n = 5
		else:
			if loyt[EIMIK]>0: return (0,l)
		
		if n == 0: return (-1,l)
		if l == EIMIK: return (0,l)
		
		if n==1 or n==3 or n==5:
			if sivu[4]==TYHJA: return (-1,l)
		else:
			if sivu[4]==l: return (-1,l)
		
		if n==6:
			if sivu[1]==TYHJA:
				if sivu[7]==l: return (-1,l)
			elif sivu[1]==l:
				if sivu[3]==l or sivu[5]==l: return (-1,l)
			
		else:
			if sivu[1]==l or sivu[3]==l or sivu[5]==l or sivu[7]==l: return (-1,l)
			
			if n == 2 or n == 3:
				if sivu[0]==TYHJA:
					if sivu[8] == l: return (-1,l)
				elif sivu[0]==l:
					if sivu[8] == TYHJA: return (-1,l)
		
		return (n,l)

	def tarkista_luvut(self):
		sivut = []
		loyt = Set()
		maar = [0,0,0,0]
		for sivu in range(6):
			(n,l) = self.tunnista(sivu)
			maar[l] += 1
			if n == -1: return False
			sivut.append(n)
			if n > 0:
				if n in loyt: return False
				loyt.add(n)
				
		#if maar[PUN]>3 or maar[VIHR]>3: return False
		if maar[PUN]>0 and maar[VIHR]>0: return False
			
		#for (a,b) in [(YLA,ALA),(OIK,VAS),(POHJA,KATTO)]:
		#	if sivut[a]>0 and sivut[b]>0 and sivut[a]+sivut[b]!=7: return False

		return True


palat = [Pala(i) for i in range(9)]

palat[0].osat[0].osat[ALA] = VIHR;
palat[0].osat[0].osat[YLA] = PUN;
palat[0].osat[1].osat[ALA] = VIHR;
palat[0].osat[1].osat[KATTO] = VIHR;
palat[0].osat[1].osat[OIK] = VIHR;
palat[0].osat[2].osat[YLA] = PUN;
palat[0].osat[2].osat[VAS] = PUN;
palat[0].osat[2].osat[POHJA] = PUN;

palat[1].osat[1].osat[KATTO] = VIHR;
palat[1].osat[1].osat[YLA] = VIHR;
palat[1].osat[1].osat[OIK] = VIHR;
palat[1].osat[2].osat[YLA] = VIHR;
palat[1].osat[2].osat[ALA] = PUN;
palat[1].osat[2].osat[VAS] = PUN;

palat[2].osat[0].osat[KATTO] = PUN;
palat[2].osat[1].osat[ALA] = VIHR;
palat[2].osat[1].osat[YLA] = PUN;
palat[2].osat[2].osat[VAS] = VIHR;
palat[2].osat[2].osat[POHJA] = VIHR;

palat[3].osat[0].osat[YLA] = VIHR;
palat[3].osat[1].osat[ALA] = PUN;
palat[3].osat[1].osat[OIK] = PUN;
palat[3].osat[2].osat[ALA] = PUN;
palat[3].osat[2].osat[POHJA] = PUN;

palat[4].osat[0].osat[ALA] = VIHR;
palat[4].osat[1].osat[OIK] = PUN;
palat[4].osat[2].osat[ALA] = VIHR;

palat[5].osat[0].osat[KATTO] = PUN;
palat[5].osat[0].osat[ALA] = PUN;
palat[5].osat[1].osat[OIK] = VIHR;
palat[5].osat[1].osat[ALA] = PUN;

palat[6].osat[0].osat[KATTO] = VIHR;
palat[6].osat[0].osat[ALA] = VIHR;
palat[6].osat[1].osat[OIK] = PUN;
palat[6].osat[2].osat[YLA] = PUN;
palat[6].osat[2].osat[POHJA] = PUN;

palat[7].osat[0].osat[KATTO] = PUN;
palat[7].osat[0].osat[ALA] = PUN;
palat[7].osat[1].osat[OIK] = VIHR;
palat[7].osat[1].osat[YLA] = VIHR;
palat[7].osat[2].osat[POHJA] = VIHR;

palat[8].osat[1].osat[OIK] = VIHR;
palat[8].osat[1].osat[YLA] = VIHR;
palat[8].osat[1].osat[ALA] = PUN;
palat[8].osat[1].osat[KATTO] = VIHR;
palat[8].osat[2].osat[ALA] = PUN;
palat[8].osat[2].osat[VAS] = PUN;
palat[8].osat[2].osat[POHJA] = PUN;

uupalat = [ p.kaannetty1().kaannetty1() for p in palat ]
palat = uupalat
kaannetyt_palat = [ p.kaannetty1().kaannetty2().kaannetty2().kaannetty2().kaannetty1() for p in palat ]

def laske_vapaat( kuutio, vanhat ):
	uudet = Set()
	mintaso = 2
	for p in vanhat:
		if kuutio.paikat[kuutio.paikka(p)]==False:
			uudet.add(p)
			mintaso = min(mintaso,p[2])
	return [uudet,mintaso]
		
ratkaisut = []
mahdolliset_palat = []

def ratkaise( kuutio, mahdolliset, vapaat, siirrot, mi, monesko ):
	if monesko == 9:
		ratkaisut.append(siirrot)
		sys.stdout.write('\rrakenteet: '+str(len(ratkaisut))+' ');
		sys.stdout.flush();
		return True
		
	vapaat,mintaso = laske_vapaat(kuutio,vapaat)
	loyt = False

	for l in xrange(mi,len(mahdolliset)):
	  (x,y,z,i,j,tas) = mahdolliset[l]
	  paik = (x,y,z)
	  if tas > mintaso: break
	  if paik in vapaat:
			p = mahdolliset_palat[l]
			if kuutio.sopiiko_pala(p):
				kuu = kuutio.kopio()
				kuu.aseta_pala(p)
				r = ratkaise(kuu, mahdolliset, vapaat, siirrot+[(x,y,z,i,j)], l+1, monesko+1)
				if r != False:
					loyt = r
					if len(ratkaisut) >= MAXRATKAISUT: return True
	return loyt
	
def rakenna( siirrot, palat ):
	k = Kuutio()
	for i in range(len(siirrot)):
			s = siirrot[i]
			x,y,z = s[:3]
			r1,r2 = s[3:5]
			p = palat[i]
			for j in range(r1): p = p.kaannetty1()
			for j in range(r2): p = p.kaannetty2()
			p = p.siirretty((x,y,z))
			k.aseta_pala(p)
	return k
	
def poista_samat( ratkaisut, palat, rot ):
	k = Kuutio()
	uniikit = []
	kuutiot = []
	for siirrot in ratkaisut:
		k = rakenna(siirrot,palat)
		ok = True
		
		if rot:
			rotaatiot = [(a,b,c) for a in range(3) for b in range(4) for c in range(2)]
		else:
			rotaatiot = [(0,0,0)]
		
		for (r1,r2,m) in rotaatiot:
			kuu = k
			if m: kuu = kuu.kaannetty1().kaannetty2().kaannetty2().kaannetty2().kaannetty1()
			for j in range(r1): kuu = kuu.kaannetty1()
			for j in range(r2): kuu = kuu.kaannetty2()

			for k2 in kuutiot:
			  vast = {}
			  eroaa = False
			  for i in range(len(kuu.paikat)):
			   if kuu.paikat[i]==False or k2.paikat[i]==False:
				   if kuu.paikat[i]!=False or k2.paikat[i]!=False:
					   eroaa = True
					   break
			   else:
				a = kuu.paikat[i].nro
				b = k2.paikat[i].nro
				if a in vast.keys():
					if vast[a] != b:
						eroaa = True
						break
				else:
					vast[a] = b
					
			  if not eroaa:
				  ok = False
				  break
					
			if not ok: break
				
		if ok:
			uniikit.append(siirrot)
			kuutiot.append(k)
			
	return uniikit

kuutio = Kuutio()
vapaat = Set([ (x,y,z) for x in range(3) for y in range(3) for z in range(3) ])
tasot = [[],[],[]]

for (x,y,z) in vapaat:
	for i in range(3):
	  for j in range(4):
		pala = palat[0]
		for k in range(i): pala = pala.kaannetty1()
		for k in range(j): pala = pala.kaannetty2()
		pala = pala.siirretty((x,y,z))
		if kuutio.sopiiko_pala(pala):
			t = pala.taso()
			tasot[t].append((x,y,z,i,j,t))
			
mahdolliset = tasot[0]+tasot[1]+tasot[2]
for l in range(len(mahdolliset)):
	(x,y,z,i,j,tas) = mahdolliset[l]
	p = palat[0]
	for k in range(i): p = p.kaannetty1()
	for k in range(j): p = p.kaannetty2()
	p = p.siirretty((x,y,z))
	mahdolliset_palat.append(p)
	

print "sijoitustavat: ",len(mahdolliset),"* 2 =", (len(mahdolliset)*2)

ratkaise(kuutio,mahdolliset,vapaat,[],0,0)
print "/ 24 =", (len(ratkaisut)/24)

#	ratkaisut = poista_samat(ratkaisut,palat,True)
#	print len(ratkaisut)

def ratkaise_varit(kuut, siirrot, monesko, mitka):
	
	if monesko == 9:
		global kuutio
		kuutio = jarjesta_uudelleen(kuut)
		print "\r--------- loytyi ---------"
		visualisoi()
		return True
	
	(x,y,z,r1,r2) = siirrot[monesko]
	
	loyt = False
	
	for i in range(9):
	  if (mitka & (0x1<<i))==0:
		for m in range(2):
			if m==1: p = kaannetyt_palat[i]
			else: p = palat[i]
			for k in range(r1): p = p.kaannetty1()
			for k in range(r2): p = p.kaannetty2()
			p = p.siirretty((x,y,z))

			kuu = kuut.kopio()
			kuu.aseta_pala(p)
			
			if kuu.tarkista_luvut():
				r = ratkaise_varit(kuu, siirrot, monesko+1, mitka | (0x1 << i))
				if r != False: loyt = r
				
	return loyt
	
def jarjesta_uudelleen(kuutio):
	vapaa = 0
	vast = {}
	uusi = kuutio.kopio()
	for z in range(3):
	 for x in range(3):
	  for y in range(3):
		paik = kuutio.paikka((x,y,z))
		nro = kuutio.paikat[paik].nro
		if nro not in vast.keys():
			vast[nro] = vapaa
			vapaa += 1
		uusi.paikat[paik].nro = vast[nro]
	return uusi





def resize(width, height):
    
	glViewport(0, 0, width, height)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(60.0, float(width)/height, .1, 1000.)
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()


class Cube(object):
    
    def __init__(self, position, color):
        
        self.position = position
        self.color = color
    
    num_faces = 6
        
    vertices = [ (0.0, 0.0, 1.0),
                 (1.0, 0.0, 1.0),
                 (1.0, 1.0, 1.0),
                 (0.0, 1.0, 1.0),
                 (0.0, 0.0, 0.0),
                 (1.0, 0.0, 0.0),
                 (1.0, 1.0, 0.0),
                 (0.0, 1.0, 0.0) ]
        
    normals = [ (0.0, 0.0, +1.0),  # front
                (0.0, 0.0, -1.0),  # back
                (+1.0, 0.0, 0.0),  # right
                (-1.0, 0.0, 0.0),  # left 
                (0.0, +1.0, 0.0),  # top
                (0.0, -1.0, 0.0) ] # bottom
    
    vertex_indices = [ (0, 1, 2, 3),  # front
                       (4, 5, 6, 7),  # back
                       (1, 5, 6, 2),  # right
                       (0, 4, 7, 3),  # left
                       (3, 2, 6, 7),  # top
                       (0, 1, 5, 4) ] # bottom    

    def render(self):                
        
        glColor( *self.color )
    
        # Adjust all the vertices so that the cube is at self.position
        vertices = [vecsum(v, self.position) for v in self.vertices]
            
        # Draw all 6 faces of the cube
        glBegin(GL_QUADS)
    
        for face_no in xrange(self.num_faces):
                        
            glNormal3dv( self.normals[face_no] )
            
            v1, v2, v3, v4 = self.vertex_indices[face_no]
                    
            glVertex( vertices[v1] )
            glVertex( vertices[v2] )
            glVertex( vertices[v3] )
            glVertex( vertices[v4] )            
        
        glEnd()
        
def visOsa( osa ):
	vari = (0.7,0.4,0.2)
	c = Cube((0,0,0),vari)
	for mika in range(6):
		if osa.osat[mika] != TYHJA:
			glPushMatrix()
			glTranslatef(0.5,0.5,0.5)
			offs = 0.8 * 0.5
			if mika == KATTO: glTranslatef(0,0,offs)
			elif mika == POHJA: glTranslatef(0,0,-offs)
			elif mika == YLA: glTranslatef(0,offs,0)
			elif mika == ALA: glTranslatef(0,-offs,0)
			elif mika == VAS: glTranslatef(-offs,0,0)
			elif mika == OIK: glTranslatef(offs,0,0)
			s2 = 0.3
			glScalef(s2,s2,s2)
			glTranslatef(-0.5,-0.5,-0.5)
			v2 = (0,0,0)
			if osa.osat[mika] == PUN: v2 = (1,0,0)
			else: v2 = (0,1,0)
			t = Cube((0,0,0),v2)
			t.render()
			glPopMatrix()
	c.render()

def visKuut( kuutio, maxnro ):
	glPushMatrix()
	glTranslate(-0.5,-0.5,-0.5)
	glScale(1/3.0,1/3.0,1/3.0)
	
	for x in range(3):
	 for y in range(3):
	  for z in range(3):
		p = kuutio.paikka((x,y,z))
		if kuutio.paikat[p] != False and kuutio.paikat[p].nro <= maxnro:
			glPushMatrix()
			glTranslatef(x,y,z)
			visOsa(kuutio.paikat[p])
			glPopMatrix()
	glPopMatrix()
    
    
initialized = False
    
SCREEN_SIZE = (800,600)
    
def initgl():
  global initialized	
  if not initialized:
	initialized = True

	print ""
	print "  ESC: pois"
	print "  ENTER: etsi seuraava ratkaisu"
	print "  SPACE: lisaa paloja"
	print "  BACKSPACE: poista paloja"
	print ""

	pygame.init()
	screen = pygame.display.set_mode(SCREEN_SIZE, pygame.HWSURFACE|pygame.OPENGL|pygame.DOUBLEBUF)
	pygame.display.set_caption('Ratkaisu')

	glShadeModel(GL_FLAT)
	glClearColor(0.5, 0.5, 0.5, 0.0)

	glEnable(GL_COLOR_MATERIAL)

	glEnable(GL_LIGHTING)
	glEnable(GL_LIGHT0)        
	glLight(GL_LIGHT0, GL_POSITION,  (0, 1, 1, 0))

	#glEnable(GL_CULL_FACE)
	glEnable(GL_DEPTH_TEST)
	glEnable(GL_NORMALIZE)

	resize(*SCREEN_SIZE)

	glMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
	
def visualisoi():
	initgl()
	maxnro = 8
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
					raise RuntimeError("quit")
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_ESCAPE:
					raise RuntimeError("quit")
				if event.key == pygame.K_RETURN:
					return
				elif event.key == pygame.K_SPACE:
					if maxnro < len(palat)-1: maxnro += 1
				elif event.key == pygame.K_BACKSPACE:
					if maxnro > 0: maxnro -= 1
		
		(ax,ay) = pygame.mouse.get_pos()
		
		x = ax/float(SCREEN_SIZE[0])*2.0 - 1.0
		y = ay/float(SCREEN_SIZE[1])*2.0 - 1.0

		# Clear the screen, and z-buffer
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

		glLoadIdentity()

		glLight(GL_LIGHT0, GL_POSITION,  (0, 1.5, -1, 1)) 

		glTranslate(0,0,-3)

		glRotate(y*180,1,0,0)
		glRotate(x*180,0,0,1)

		visKuut( kuutio, maxnro )

		time.sleep(1/50.0)
	
		# Show the screen
		pygame.display.flip()

try:
	no = MINHAKU+1
	for siirrot in ratkaisut[MINHAKU:]:
		r = ratkaise_varit(Kuutio(),siirrot,0,0)
		sys.stdout.write("\rhaku: "+str(no)+"/"+str(len(ratkaisut)))
		sys.stdout.flush()
		no += 1

	if kuutio == False:
		raise RuntimeError("Ei ratkennut")
		
except RuntimeError: pass

