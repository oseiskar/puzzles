#!/usr/bin/python

import sys
import pygame
import time
import random
import math
from OpenGL.GL import *
from OpenGL.GLU import *

pala_id = 0

class Pala:

	def __init__(self,palikat,varit,id = -1):
		if id == -1:
			global pala_id
			self.id = pala_id
			pala_id = pala_id + 1
		else:
			self.id = id
		self.pset = frozenset(palikat)
		self.palikat = palikat
		self.varit = varit
		self.hsh = frozenset( str(self.palikat[i])+str(self.varit[i]) for i in range(len(self.palikat)) ).__hash__()

	def kaannetty1(self):
		palikat = []
		for i in range(len(self.palikat)):
			palikat.append( ( self.palikat[i][0], -self.palikat[i][2], self.palikat[i][1] ) )
		return Pala(palikat,self.varit,self.id)

	def kaannetty2(self):
		palikat = []
		for i in range(len(self.palikat)):
			palikat.append( ( self.palikat[i][1], -self.palikat[i][0], self.palikat[i][2] ) )
		return Pala(palikat,self.varit,self.id)
			
	def siirretty(self,p):
		palikat = [ vecsum(self.palikat[i],p) for i in range(len(self.palikat)) ]
		return Pala(palikat,self.varit,self.id)
		
	def normalisoitu(self,order):
		
		zm = min( p[order[0]] for p in self.palikat )
		ym = min( p[order[1]] for p in self.palikat if p[order[0]] == zm )
		xm = min( p[order[2]] for p in self.palikat if p[order[0]] == zm and p[order[1]] == ym )
		p = [0,0,0]
		p[order[0]] = -zm
		p[order[1]] = -ym
		p[order[2]] = -xm
		return self.siirretty(tuple(p))
		
	def posit( self ):
		o = tuple( -min(p[i] for p in self.palikat) for i in range(3) )
		return self.siirretty( o )
		
	def hash(self):
		return self.hsh
		
	def kaikki_asemat(self,perm):
		asemat = []
		keys = set()
		
		p1 = self
		for i in range(4):
			p2 = p1
			for j in range(4):
				p3 = p2
				for k in range(4):
					p = p3.normalisoitu(perm)
					key = p.hash()
					if key not in keys:
						asemat.append( p )
						keys.add( key )
					p3 = p3.kaannetty1()
				p2 = p2.kaannetty2()
			p1 = p1.kaannetty1()

		return asemat

def vecsum(v1,v2):
	return ( v1[0]+v2[0], v1[1]+v2[1], v1[2]+v2[2] )

class Rakenne:
	MAXSZ = 9
	
	MUSTA = 1
	VAALEA = 2
	EIKAY = 3
	KUMPIVAAN = 0
	PITAAOLLAMUSTA = -1
	PITAAOLLAVAALEA = -2
	
	NUM_VARIAATIOT = 11

	def __init__(self, variaatio):
		self.perm = [0,1,2]
		self.paikat = [self.EIKAY]*(self.MAXSZ**3)
		self.sapluuna( variaatio )
		self.variaatio = variaatio
		self.invp = [0,0,0]
		for i in range(3):
			self.invp[self.perm[i]] = i
		
	def sapluuna( self, variaatio ):
		
		kaikkipaikat = [(x,y,z) for x in range(self.MAXSZ) for y in range(self.MAXSZ) for z in range(self.MAXSZ)] 
		
		for (x,y,z) in kaikkipaikat:
			paik = self.paikka((x,y,z))
			vari = -((x+y+z)%2 + 1)
			sisa = False
			pala = False
		
			if variaatio==1:
				self.perm = [1,0,2]
				pala = x < 7 and y < 6 and z < 2
							
			elif variaatio==2:
				self.perm = [2,1,0]
				if x < 4 and y < 4 and z < 6:
					pala = True
					sisa = (x > 0 and x < 3 and y > 0 and y < 3)
					
					if z == 5:
						if sisa:
							sisa = False
							pala = True
						else: pala = False
									
			elif variaatio==3:
				self.perm = [2,1,0]
				pala = x < 7 and y < 7 and z < 4 and x >= z and x < 7-z and y >= z and y < 7-z
				sisa = (x > z and x < 7-z-1 and y > z and y < 7-z-1)
				vari = -((x+y+z+1)%2 + 1)
				
			elif variaatio==4:
				self.perm = [1,0,2]
				
				if x < 6 and y < 6 and z < 4 and ((x < 2 or x >= 4) or (y < 2 or y >= 4)):
					if ((x < 2 or x >= 4) and (y < 2 or y >= 4)) or z < 2:
						if ((x < 1 or x >= 5) and (y < 1 or y >= 5)) or z < 3:
							pala = True
								
			elif variaatio==5:
				pala =  x < 6 and y < 4 and z <= x
						
			elif variaatio==6:
				pala = (x < 9 and y < 4 and z <= 4) and ((x==4 and z == 3) or (x != 4 and z <= min(x, 8-x)))
				
			elif variaatio==7:
				pala = x < 6 and y < 5 and z < 3 and (y != 2 or x not in [2,3])
				
			elif variaatio==8:
				if x < 6 and y < 5 and z < 4 and (y != 2 or x not in [2,3]):
					if (x in [2,3] and z<3) or (x<2 and z < 2) or (x > 3):
						pala = True
							
			elif variaatio==9:
				if x < 8 and y < 4 and z < 4 and x not in [3,4]:
					if x < 3 or z < 3:
						pala = True
							
			elif variaatio==10:
				if x < 6 and y < 6 and z < 3:
					if x not in [2,3] or y < 2:
						pala = True

			elif variaatio==11:
				if x < 6 and y < 6 and z < 6:
					if (x < 2 or y < 2):
						if z < 3 or (x<3 and y<3):
							pala = True
							
			if pala:
				if sisa: self.paikat[paik] = self.KUMPIVAAN
				else: self.paikat[paik] = vari
				

	def numneigh(self,p):
		n = 0
		for i in range(3):
			for d in [-1,1]:
				p2 = [p[j] for j in range(3)]
				p2[i] += d
				if self.vapaa(tuple(p2)): n += 1
		return n
		
	def kaikkipalat(self):
		kaikkipaikat = [(x,y,z) for x in range(self.MAXSZ) for y in range(self.MAXSZ) for z in range(self.MAXSZ)]
		return [p for p in kaikkipaikat if self.kuuluurakenteeseen(p)]
		
	def permute(self,i1,i2,i3):
		p = (i1,i2,i3)
		return (p[self.invp[0]],p[self.invp[1]],p[self.invp[2]])
		
	def jarjestys( self ):
		jarj = []
		
		for i1 in range(self.MAXSZ):
			for i2 in range(self.MAXSZ):
				for i3 in range(self.MAXSZ):
					(x,y,z) = self.permute(i1,i2,i3)
					v = self.paikat[self.paikka((x,y,z))]
					if v <= 0:
						jarj.append((x,y,z))
		
		return jarj
		
	def sopivat_asemat( self, kaikki_asemat, jarj ):
		sopivat_as = []
		sopivat_jarj = [[] for j in range(len(jarj))]
		for pa in kaikki_asemat:
			ps = []
			for a in pa:
				for j in range(len(jarj)):
					for paik in a.pset:
						d = tuple( jarj[j][i]-paik[i] for i in range(3) )
						a1 = a.siirretty(d)
						assert( jarj[j] in a1.pset )
						if self.sopiiko_pala(a1):
							ps.append((j,a1))
							sopivat_jarj[j].append(a1)
			sopivat_as.append(ps)
		return (sopivat_as,sopivat_jarj)
		

	def kopio(self):
		uusi = Rakenne(0)
		uusi.paikat = self.paikat[:]
		return uusi
		
	def realisoi(self):
		uusi = self.kopio()
		for i in range(self.MAXSZ**3):
			if uusi.paikat[i] <= 0:
				uusi.paikat[i] = -uusi.paikat[i]
		return uusi

	def sopiiko_pala(self,pala):
		for i in range(len(pala.palikat)):
			p = pala.palikat[i]
			if not self.sopiiko_vari(p,pala.varit[i]): return False
		return True
		
	def aseta_pala(self,pala):
		for i in range(len(pala.palikat)):
			self.paikat[self.paikka(pala.palikat[i])] = pala.varit[i]

	def paikka(self,p):
		return p[0]*self.MAXSZ*self.MAXSZ + p[1]*self.MAXSZ + p[2]
		
	def validi(self,p):
		if p[0] < 0 or p[0] >= self.MAXSZ: return False
		if p[1] < 0 or p[1] >= self.MAXSZ: return False
		if p[2] < 0 or p[2] >= self.MAXSZ: return False
		return True
		
	def vapaa(self,p):
		if not self.validi(p): return False
		return self.paikat[self.paikka(p)] <= 0
		
	def kuuluurakenteeseen(self,p):
		if not self.validi(p): return False
		return self.paikat[self.paikka(p)] != self.EIKAY
		
	def varattu(self,p):
		if not self.validi(p): return False
		return self.paikat[self.paikka(p)] in [self.MUSTA, self.VAALEA]
		
	def sopiiko_vari( self, p, vari ):
		if not self.validi(p): return False
		v = self.paikat[self.paikka(p)]
		if v > 0: return False
		if v == self.KUMPIVAAN: return True
		return v == -vari

def rakenna( sijoitetut_palat ):
	r = Rakenne(0)
	for p in sijoitetut_palat:
		r.aseta_pala( p )
	return r
		
def resize(width, height):
    
	glViewport(0, 0, width, height)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(60.0, float(width)/height, .1, 1000.)
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()

    
def renderCube(position, color):                
        
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
	
	glColor( *color )

	# Adjust all the vertices so that the cube is at self.position
	vertices = [vecsum(v, position) for v in vertices]
		
	# Draw all 6 faces of the cube
	glBegin(GL_QUADS)

	for face_no in xrange(num_faces):
					
		glNormal3dv( normals[face_no] )
		
		v1, v2, v3, v4 = vertex_indices[face_no]
				
		glVertex( vertices[v1] )
		glVertex( vertices[v2] )
		glVertex( vertices[v3] )
		glVertex( vertices[v4] )            
	
	glEnd()
        
def visOsa( kumpivari ):
	if kumpivari == 1: # Musta
		vari = (0.4,0.2,0.1) #(0.7,0.4,0.2)
	elif kumpivari == 2: # Vaalea
		vari = (0.8,0.6,0.3)
	elif kumpivari == 0: # Kumpi vaan
		vari = (0.9,0.6,0.6)
		
	renderCube((0,0,0),vari)

def visRak( rakenne, cm ):
	glPushMatrix()
	glScale(1/3.0,1/3.0,1/3.0)
	glTranslate(-cm[0], -cm[1], 0)
	glTranslate(-0.5,-0.5,0)
	#glTranslate(-cm[0], -cm[1], -cm[2])
	#glTranslate(-0.5,-0.5,-0.5)
	
	for x in range(rakenne.MAXSZ):
		for y in range(rakenne.MAXSZ):
			for z in range(rakenne.MAXSZ):
				v = rakenne.paikat[rakenne.paikka((x,y,z))]
				if v in [0,1,2]:
					glPushMatrix()
					glTranslatef(x,y,z)
					visOsa(v)
					glPopMatrix()
	glPopMatrix()
	
    
initialized = False
    
SCREEN_SIZE = (800,600)
    
def initgl():
	global initialized	
	if not initialized:
		initialized = True

	pygame.init()
	screen = pygame.display.set_mode(SCREEN_SIZE, pygame.HWSURFACE|pygame.OPENGL|pygame.DOUBLEBUF)
	pygame.display.set_caption('Ratkaisu')

	#glShadeModel(GL_FLAT)
	glShadeModel(GL_SMOOTH)
	glClearColor(0.5, 0.5, 0.5, 0.0)

	glEnable(GL_COLOR_MATERIAL)

	glEnable(GL_LIGHTING)
	glEnable(GL_LIGHT0)        
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

	#glLight(GL_LIGHT0, GL_POSITION,  (0, 1, 1, 0))
	#glEnable(GL_CULL_FACE)
	glEnable(GL_DEPTH_TEST)
	glEnable(GL_NORMALIZE)

	resize(*SCREEN_SIZE)

	glMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
	
def seqvecsum( seq ):
	return tuple( [ sum( [ s[i] for s in seq ] ) for i in range(3) ] )
	
def seqvecavg( seq ):
	return tuple( [ s/float(len(seq)) for s in seqvecsum( seq ) ] )
	
def flatp( palat ):
	l = []
	for p in palat:
		l = l + p.palikat
	return l
	
def rakennusjarjestys( palat ):
	rakenne = Rakenne(0)
	uudet = []
	while len(palat):
		mika = 0
		for i in range(len(palat)):
			for (x,y,z) in palat[i].palikat:
				if z > 0 and not rakenne.varattu((x,y,z-1)) and set([(x,y,z-1),(x,y,z-2)]).isdisjoint( palat[i].pset ):
					break
			else:
				mika = i
				break
		
		uudet.append(palat[mika])
		rakenne.aseta_pala(palat[mika])
		del palat[mika]
	
	return uudet
			
	
def visualisoi( sijoitetut_palat, rakenne0, reflection = True ):
	initgl()
	maxnro = len(sijoitetut_palat)
	muuttunut = True
	vainviim = False
	
	if len(sijoitetut_palat):
		cm = seqvecavg( flatp( sijoitetut_palat ) )
	else:
		cm = seqvecavg( rakenne0.kaikkipalat() )
	
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
					raise RuntimeError("quit")
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_ESCAPE:
					raise RuntimeError("quit")
				if event.key == pygame.K_RETURN:
					return False
				elif event.key == pygame.K_SPACE:
					if len(sijoitetut_palat) == 0:
						return True
					if maxnro < len(sijoitetut_palat):
						maxnro += 1
						muuttunut = True
				elif event.key == pygame.K_BACKSPACE:
					if maxnro > 0:
						maxnro -= 1
						muuttunut = True
				elif event.key == pygame.K_v:
					vainviim = vainviim == False
					muuttunut = True
			
		if muuttunut:
			muuttunut = False
			#rakenne = rakenna( [sijoitetut_palat[maxnro-1]] )
			if len(sijoitetut_palat):
				if vainviim:
					if maxnro > 0:
						rakenne = rakenna( [sijoitetut_palat[maxnro-1]] )
					else:
						rakenne = rakenna( [] )
				else:
					rakenne = rakenna( sijoitetut_palat[:maxnro] )
			else:
				#rakenne = rakenne0
				rakenne = rakenne0.realisoi()
			glNewList( 1, GL_COMPILE )
			visRak( rakenne, cm )
			glEndList()
		
		(ax,ay) = pygame.mouse.get_pos()
		
		x = ax/float(SCREEN_SIZE[0])*2.0 - 1.0
		y = (ay/float(SCREEN_SIZE[1])*2.0 - 2.0) / 2

		# Clear the screen, and z-buffer
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

		glLoadIdentity()

		camdist = 4
		glLight(GL_LIGHT0, GL_POSITION,  (0, 1.5, -1, 1)) 

		glTranslate(0, 0, -camdist)
		glRotate(y*180,1,0,0)
		glRotate(x*180,0,0,1)

		#visRak( rakenne, cm )
		
		camh = (cm[2]-0.5)/3.0
		glTranslate( 0,0, -camh )
		
		if reflection and math.cos(y*math.pi)*camdist > -camh:
			glScale(1,1,-1)
			glCallList( 1 )
			
			glPushMatrix()
			glLoadIdentity()
			glEnable(GL_BLEND)
			glDisable(GL_LIGHTING)
			glDisable(GL_DEPTH_TEST)
			glBegin(GL_QUADS)
			alpha1 = 0.8
			alpha2 = 0.99
			glColor( 0.5, 0.5, 0.5, alpha1 )
			glVertex(-1,1,-1 )
			glVertex(1,1,-1 )
			glColor( 0.55, 0.55, 0.55, alpha2 )
			glVertex(1,-1,-1 )
			glVertex(-1,-1,-1 )
			glEnd()
			glEnable(GL_LIGHTING)
			glEnable(GL_DEPTH_TEST)
			glDisable(GL_BLEND)
			glPopMatrix()
			glScale(1,1,-1)
		
		glCallList( 1 )

		time.sleep(1/50.0)
	
		# Show the screen
		pygame.display.flip()

def ratkaise( paikka_no, paikat, sopivat_paik, sopivat_as, rakenne, nyk ):

	assert( paikka_no < len(sopivat_paik) )
	
	for a in sopivat_paik[paikka_no]:
		
			assert( paikat[paikka_no] in a.pset )
			assert( rakenne.sopiiko_pala( a ) )
			
			rakenne1 = rakenne.kopio()
			rakenne1.aseta_pala( a )
							
			assert( not rakenne1.vapaa( paikat[paikka_no] ) )
			
			paikka_no1 = paikka_no
			while not rakenne1.vapaa( paikat[paikka_no1] ):
				paikka_no1 += 1
				if paikka_no1 == len(paikat):
					visualisoi( rakennusjarjestys( nyk+[a] ), rakenne )
					return [a]
			
			sopivat_as1 = sopivat_as[:]
			ok = True
			
			for i in range(len(sopivat_as1)):
				
				if len(sopivat_as1[i]) == 0:
					assert( False )
					break
				elif sopivat_as1[i][0][1].id == a.id:
					del sopivat_as1[i]
					break
			else:
				assert( False )
					
			sopivat_paik1 = [[]]*(paikka_no1)
			assert( len(sopivat_paik1) == paikka_no1 )
			
			for i in range(paikka_no1,len(sopivat_paik)):
				assert( i == len(sopivat_paik1) )
				sp = [a1 for a1 in sopivat_paik[i] if a1.id != a.id and a.pset.isdisjoint(a1.pset)]
				if len(sp) == 0 and rakenne1.vapaa( paikat[i] ):
					ok = False
					break
				sopivat_paik1.append(sp)
				
			if not ok:
				continue
				
			assert( len(sopivat_paik1) == len(sopivat_paik) )
			
			for i in range(len(sopivat_as1)):
				as1 = []
				for (j,a2) in sopivat_as1[i]:
					if a2.pset.isdisjoint( a.pset ):
						as1.append( (j,a2) )
				if len(as1) == 0:
					ok = False
					break
				sopivat_as1[i] = as1
						
			if not ok:
				continue
					
			#if len(sopivat_as1) == 2:
			#	return [a]
					
			assert( len(sopivat_paik1) == len(sopivat_paik) )
					
			r = ratkaise( paikka_no1, paikat, sopivat_paik1, sopivat_as1, rakenne1, nyk + [a] )
			
			#if r != False:
			#	return [a] + r
	else:
		return False
		
M = Rakenne.MUSTA
V = Rakenne.VAALEA

palat = [
	Pala( [(0,0,0)], [M] ),
	Pala( [(0,0,0),(1,0,0)], [M,V] ),
	Pala( [(0,0,0),(1,0,0)], [M,V] ),
	Pala( [(0,0,0),(1,0,0),(2,0,0)], [M,V,M] ),
	Pala( [(0,0,0),(1,0,0),(2,0,0)], [V,M,V] ),
	Pala( [(0,0,0),(1,0,0),(2,0,0)], [V,M,V] ),
	Pala( [(0,0,0),(1,0,0),(1,1,0),(2,1,0)], [M,V,M,V] ),
	Pala( [(0,0,0),(1,0,0),(1,1,0),(2,1,0)], [M,V,M,V] ),
	Pala( [(0,0,0),(1,0,0),(1,1,0),(0,0,1)], [M,V,M,V] ),
	Pala( [(0,0,0),(1,0,0),(1,1,0),(1,1,1)], [M,V,M,V] ),
	Pala( [(0,0,0),(1,0,0),(0,1,0),(0,0,1)], [V,M,M,M] ),
	Pala( [(0,0,0),(1,0,0),(2,0,0),(3,0,0)], [V,M,V,M] ),
	Pala( [(0,0,0),(1,0,0),(2,0,0),(3,0,0),(1,1,0)], [V,M,V,M,V] ),
	Pala( [(0,0,0),(1,0,0),(2,0,0),(2,1,0),(2,2,0)], [M,V,M,V,M] ),
	Pala( [(0,0,0),(1,0,0),(2,0,0),(2,1,0),(0,1,0)], [M,V,M,V,V] ),
	Pala( [(0,0,0),(1,0,0),(2,0,0),(2,1,0),(0,1,0)], [V,M,V,M,M] ),
	Pala( [(0,0,0),(1,0,0),(0,1,0),(1,1,0),(1,1,1)], [V,M,M,V,M] ),
	Pala( [(0,0,0),(1,0,0),(0,1,0),(1,1,0),(2,1,0)], [V,M,M,V,M] ),
	Pala( [(0,0,0),(1,0,0),(2,0,0),(2,0,1),(2,1,1)], [M,V,M,V,M] ),
	Pala( [(0,0,0),(1,0,0),(2,0,0),(2,0,1),(0,1,0)], [M,V,M,V,V] ),
	Pala( [(1,1,0),(1,0,0),(0,1,0),(1,1,1),(1,2,0),(2,1,0)], [M,V,V,V,V,V] )
	]
	
palat = palat[::-1]
#random.shuffle(palat)
	



try:
	
	print ""
	print "  ESC: pois"
	print "  ENTER: etsi seuraava ratkaisu"
	print "  SPACE: lisaa paloja / seuraava variaatio"
	print "  BACKSPACE: poista paloja"
	print "  V: vain viimeinen pala"
	print ""
	
	variaatio = 1
	rakenne0 = Rakenne( variaatio )
	
	while visualisoi( [], rakenne0 ):
		variaatio += 1
		if variaatio > Rakenne.NUM_VARIAATIOT:
			variaatio = 1
		rakenne0 = Rakenne( variaatio )
	
	jarjestys = rakenne0.jarjestys()
	palojen_asemat = [ p.kaikki_asemat(rakenne0.perm) for p in palat ]

	(sopivat_as,sopivat_jarj) = rakenne0.sopivat_asemat( palojen_asemat, jarjestys )
	
	sijoitetut_palat = ratkaise( 0, jarjestys, sopivat_jarj, sopivat_as, rakenne0, [] )
	#sijoitetut_palat = []
	#sijoitetut_palat = palat
	#sijoitetut_palat = [p[-1] for p in sopivat_jarj[:20]]
	#sijoitetut_palat = [p.posit() for p in palat[5].kaikki_asemat()]
	#sijoitetut_palat = [ [p.posit() for p in palat[i].kaikki_asemat()] for i in range(len(palat)) if len(palat[i].kaikki_asemat()) == 12 ][1]

	if sijoitetut_palat:
		visualisoi( sijoitetut_palat, rakenne0 )
	else:
		print "Ei uusia ratkaisuja"
		visualisoi( [], rakenne0 )
except RuntimeError:
	pass
	
