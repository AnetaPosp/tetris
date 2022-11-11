# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 19:47:00 2018

@author: spravce
"""

from tkinter import *
import random

# definice tvarů ze 4 kostek a jejich pohybů a chování v hracím poli
class square(object):

    def __init__(self, root, canvas):
        """
        vytvoří pohyblivý tvar do hry
        základní tvar je čtverec, ostatní viz definice dole
        coordinateList: [(x1,y1),(x2,y2),(x3,y3),(x4,y4)] souřadnice čtverečků tvořících tvar
        """
        self.default_coordinates=[(w/2-1,0),(w/2-1,1),(w/2,0),(w/2,1)]
        self.color="violet"
        self.restOfInit(root,canvas)
    
    def restOfInit(self,root,canvas):
        """
        jak má pokračovat init, obecná funkce pro jakýkoliv tvar
        přiřazení základních charakteristik tvaru, vytvoření jeho obrazu v canvas
        kontrola, zda někde nenaráží na už přítomnou kostičku
        tvorba šipek k ovládání a funkce samovolného pohybu dolů
        """                
        self.state=1 #v jaké rotační poloze je. není důležité u čtverce, ale ostatní odvinuté tvary to potřebují
        self.root=root
        self.canvas=canvas
        self.coordinateList=self.default_coordinates[:]
        self.createImage(self.coordinateList)
        
        for coordinate in self.default_coordinates:
            if coordinate in forbidden_coordinates:
                self.game_over()
                return 0 #jen aby init nepokračoval dál
        
        self.bindArrows()
        self.letItFall()
        
    def game_over(self):
        """
        zneaktivní stávající šipky a vytvoří okno s hláškou game over
        """
        newWindow=Toplevel(self.root)
        l=Label(newWindow,text="GAME OVER")
        b=Button(newWindow,text="EXIT",command=self.root.destroy)
        l.pack()
        b.pack()
        
    def letItFall(self):
        """
        vytvoří list s časovači. první časovač posune tvar dolů za 1*n s, další za 2*n s... od initu
        časovačů se udělá h - neb tvar potřebuje spadnout max. h-krát než se dostane na dno
        """
        global shape_count
        n=shape_count/50+1 #rychlostní koeficient. hra se postupně zrychluje
        
        self.timers=[]
        for time in range(h):
            self.timers.append(self.canvas.after(int((1/n)*(time+1)*1000),self.moveDown))

    def bindArrows(self):
        """
        sváže pohyb s šipkama na klávesnici
        """
        self.root.bind("<Left>",self.keyLeft)
        self.root.bind("<Right>",self.keyRight)
        self.root.bind("<Up>",self.keyUp)
        self.root.bind("<Down>",self.keyDown)
        
    def unbindArrows(self):
        """
        odváže pohyb od kliků na šipky na klávesnici
        """
        self.root.unbind("<Left>")
        self.root.unbind("<Right>")
        self.root.unbind("<Up>")
        self.root.unbind("<Down>")
        
    def createImage(self,coordinateList):
        """
        smaže předchozí aktivní tvar, pokud není(začátek tahu), jen nakreslí nový
        """
        try:
            for i in range(4):
                self.canvas.delete(self.imageList[i][0])
        except AttributeError:
            pass
        self.imageList=[]
        for coordinates in self.coordinateList:
            #pro každou koordinátu v tvaru udělá čtvereček a zapíše ho do imageList
            #spolu se souřadnicemi
            x,y=coordinates
            image=self.canvas.create_rectangle(x*s,y*s,(x+1)*s,(y+1)*s,fill=self.color)
            self.imageList.append((image,x,y,self.color))
        self.root.update() 
        
    def moveDown(self):
        global inactive_shapes
        global forbidden_coordinates
        global shape_count
        global points
        
        newCoordinates=[] #hypotetické nové souřadnice
        possible=True
        for coordinates in self.coordinateList:
            x,y=coordinates
            new_y=y+1
            #podívá se, jestli je pohyb každého ze čtverečků povolený:
            possible=possible and self.movePossible(x,new_y)
            newCoordinates.append((x,new_y)) #do nových souřadnic dá každý čtvereček
        if possible==True: #pokud je pohyb všech možný, přepíše koordináty
            self.coordinateList=newCoordinates
            self.createImage(newCoordinates)
        else:
            """
            pokud není možný pohyb  dolů, tvar zneaktivní a nahoře se vytvoří nový
            """
            shape_count+=1
            # vypnutí šipek: aby se nedal udělat další pohyb
            self.unbindArrows()
#           vypnutí současných timerů
            for timer in self.timers:
                self.canvas.after_cancel(timer)
            #uloží spadlý tvar + koordináty  
            inactive_shapes=inactive_shapes+self.imageList[:] 
            for coordinates in self.coordinateList:
                x,y=coordinates
                forbidden_coordinates.append(coordinates)
            self.cleanFullLine()
#            vznik nového tvaru
            startNewShape(self.root,self.canvas)     
            
    def keyDown(self,event):
        """
        aby šel moveDown svázat se šipkou
        """
        self.moveDown()
            
    def cleanFullLine(self):
        """
        podívá se na každý řádek v hracím poli (souřadnice y = 0 až h)
        pro každé y se podívá, kolik čtverečků leží v řádku y
        pokud je počet ==w, je řádek plný a je třeba ho smazat a čtverečky nad ním posunout dolů
        mazání: z listu inactive shapes, z forbidden coodrinates, z canvas
        posouvání: také u všech tří věcí
        """
        global inactive_shapes
        global forbidden_coordinates
        
        full_lines=0 #počítadlo, kolik řádků se při tahu zaplnilo
        for y in range(h): # pro každý řádek se udělá kontrola
            count=0 #počet neaktivních čtverečků se stejnou y souřadnicí
            for shape in inactive_shapes: #shape: (rectangle_id, x,y,color)
                if shape[2]==y:
                    count+=1
                    
            if count==w: #pokud je některý řádek plný
                full_lines+=1
                iterable=inactive_shapes[:]
                for shape in iterable: #kopie inactive_shapes, přes kterou se iteruje
                    if shape[2]==y:
                        self.canvas.delete(shape[0]) #zničí všechny kostky na daném řádku
                        inactive_shapes.remove(shape)
                    elif shape[2]<y: #pokud je souřadnice nad zničeným řádkem, přepíše se o 1 níž
                        inactive_shapes.remove(shape)
                        self.canvas.delete(shape[0])
                        r=self.canvas.create_rectangle(s*(shape[1]),s*(shape[2]+1),s*(shape[1]+1),s*(shape[2]+2),fill=shape[3])
                        movedDown=(r,shape[1],shape[2]+1,shape[3]) #nový tvar, posunutý o 1 dolů
                        inactive_shapes.append((movedDown))
                        
        forbidden_coordinates=[]
        for shape in inactive_shapes:
            forbidden_coordinates.append((shape[1],shape[2]))
        self.root.update()
        updateScore(self.root,full_lines)
            
    def moveLeft(self):
        newCoordinates=[] #hypotetické nové souřadnice
        possible=True
        for coordinates in self.coordinateList:
            x,y=coordinates
            new_x=x-1
            #podívá se, jestli je pohyb každého ze čtverečků povolený:
            possible=possible and self.movePossible(new_x,y)
            newCoordinates.append((new_x,y)) #do nových souřadnic dá každý čtvereček
        if possible==True: #pokud je pohyb všech možný, přepíše koordináty
            self.coordinateList=newCoordinates
            self.createImage(newCoordinates)
            
    def keyLeft(self,event):
        """
        aby šel moveLeft svázat se šipkou
        """
        self.moveLeft()
            
    def moveRight(self):
        newCoordinates=[] #hypotetické nové souřadnice
        possible=True
        for coordinates in self.coordinateList:
            x,y=coordinates
            new_x=x+1
            #podívá se, jestli je pohyb každého ze čtverečků povolený:
            possible=possible and self.movePossible(new_x,y)
            newCoordinates.append((new_x,y)) #do nových souřadnic dá každý čtvereček
        if possible==True: #pokud je pohyb všech možný, přepíše koordináty
            self.coordinateList=newCoordinates
            self.createImage(newCoordinates)
            
    def keyRight(self,event):
        """
        aby šel moveRight svázat se šipkou
        """
        self.moveRight()
    
    def movePossible(self,x,y):
        global forbidden_coordinates
        isPossible=True
        # podívá se, zda není koordináta mimo hrací pole
        if x>w-1 or x<0 or y>h-1:
            isPossible=False
        #a zda není zabraná neaktivním tvarem (jedna z forbidden coordinates)
        isPossible=isPossible and ((x,y) not in forbidden_coordinates)
        return isPossible   
            
    def rotate(self):
        pass
    
    def keyUp(self,event):
        """
        aby šel rotate svázat se šipkou
        """
        self.rotate()
        
class Z(square):
    """
    vytvoří pohyblivý tvar do hry, tvar Z
    oproti čtverci má i rotaci
    """
    def __init__(self, root, canvas):
        self.default_coordinates=[(w/2-1,0),(w/2,0),(w/2,1),(w/2+1,1)]
        self.color="salmon"
        self.restOfInit(root,canvas)
        
    def findRotatedCoords(self):
        """
        najde hypotetické souřadnice po rotaci
        """
        a,b,c,d=self.coordinateList #souřadnice jednotlivých kostek
        if self.state==1:
            #jak se souřadnice změní, když je tvar otočí. v případě nejasností nakresli
            newCoordList=[(a[0]+2,a[1]),d,c,(b[0],b[1]+2)]
            temp=2  #přehazováí rotačních stavů 1 a 2
        else:
            newCoordList=[(a[0]-2,a[1]),(d[0],d[1]-2),c,b]
            temp=1
        return newCoordList, temp
        
    def rotate(self):
        """
        zkontroluje, zda jsou souřadnice po rotaci OK a příp. provede
        """
        newCoordList, temp=self.findRotatedCoords()
        possible=True
        for coordinate in newCoordList: #kontrola, že teor. nové koord pro všechny kostky jsou povolené
            teor_x,teor_y=coordinate
            possible=possible and self.movePossible(teor_x,teor_y)
        if possible==True:  
            self.coordinateList=newCoordList
            self.state=temp #rotační stav se změní na nový
            self.createImage(newCoordList)
        
class S(Z):
    """
    vytvoří pohyblivý tvar do hry, tvar S
    dědí funkci rotate od Z, jinak vše jako nadřazený square
    """
    def __init__(self, root, canvas):
        self.default_coordinates=[(w/2-1,0),(w/2,0),(w/2-2,1),(w/2-1,1)]
        self.color="orange"
        self.restOfInit(root,canvas)
        
    def findRotatedCoords(self):
        a,b,c,d=self.coordinateList #souřadnice jednotlivých kostek
        if self.state==1:
            #jak se souřadnice změní, když je tvar otočí. v případě nejasností nakresli
            newCoordList=[(a[0]-1,a[1]),(b[0]-1,b[1]+2),c,d]
            temp=2 
        else:
            newCoordList=[(a[0]+1,a[1]),(b[0]+1,b[1]-2),c,d]
            temp=1
        return newCoordList, temp
    
class L(Z):
    """
    vytvoří pohyblivý tvar do hry, tvar L
    """
    def __init__(self, root, canvas):
        self.default_coordinates=[(w/2-1,1),(w/2-1,0),(w/2-1,2),(w/2,2)]
        self.color="black"
        self.restOfInit(root,canvas)
        
    def findRotatedCoords(self):
        a,b,c,d=self.coordinateList #souřadnice jednotlivých kostek
        if self.state==1:
            #jak se souřadnice změní, když je tvar otočí. v případě nejasností nakresli
            newCoordList=[a,(b[0]+1,b[1]+1),(c[0]-1,c[1]-1),(d[0]-2,d[1])]
            temp=2 
        elif self.state==2:
            newCoordList=[a,(b[0]-1,b[1]+1),(c[0]+1,c[1]-1),(d[0],d[1]-2)]
            temp=3
        elif self.state==3:
            newCoordList=[a,(b[0]+1,b[1]-1),(c[0]-1,c[1]+1),(d[0]+2,d[1])]
            temp=4 
        else:
            newCoordList=[a,(b[0]-1,b[1]-1),(c[0]+1,c[1]+1),(d[0],d[1]+2)]
            temp=1
        return newCoordList, temp
        
class reversedL(Z):
    """
    vytvoří pohyblivý tvar do hry, tvar obrácené L
    """
    def __init__(self, root, canvas):
        self.default_coordinates=[(w/2,1),(w/2,0),(w/2,2),(w/2-1,2)]
        self.color="blue"
        self.restOfInit(root,canvas)
        
    def findRotatedCoords(self):
        a,b,c,d=self.coordinateList #souřadnice jednotlivých kostek
        if self.state==1:
            #jak se souřadnice změní, když je tvar otočí. v případě nejasností nakresli
            newCoordList=[a,(b[0]+1,b[1]+1),(c[0]-1,c[1]-1),(d[0],d[1]-2)]
            temp=2 
        elif self.state==2:
            newCoordList=[a,(b[0]-1,b[1]+1),(c[0]+1,c[1]-1),(d[0]+2,d[1])]
            temp=3
        elif self.state==3:
            newCoordList=[a,(b[0]+1,b[1]-1),(c[0]-1,c[1]+1),(d[0],d[1]+2)]
            temp=4 
        else:
            newCoordList=[a,(b[0]-1,b[1]-1),(c[0]+1,c[1]+1),(d[0]-2,d[1])]
            temp=1
        return newCoordList, temp

class I(Z):
    """
    vytvoří pohyblivý tvar do hry, tyčka
    """
    def __init__(self, root, canvas):
        self.default_coordinates=[(w/2-1,0),(w/2-1,1),(w/2-1,2),(w/2-1,3)]
        self.color="green"
        self.restOfInit(root,canvas)
        
    def findRotatedCoords(self):
        a,b,c,d=self.coordinateList #souřadnice jednotlivých kostek
        if self.state==1:
            #jak se souřadnice změní, když je tvar otočí. v případě nejasností nakresli
            newCoordList=[(b[0]-1,b[1]),b,(b[0]+1,b[1]),(b[0]+2,b[1])]
            temp=2 
        else:
            newCoordList=[(b[0],b[1]-1),b,(b[0],b[1]+1),(b[0],b[1]+2)]
            temp=1
        return newCoordList, temp
    
class triangle(Z):
    """
    vytvoří pohyblivý tvar do hry, tři v řadě a jedna uprostřed
    """
    def __init__(self, root, canvas):
        self.default_coordinates=[(w/2,1),(w/2-1,1),(w/2,0),(w/2+1,1)]
        self.color="red"
        self.restOfInit(root,canvas)
        
    def findRotatedCoords(self):
        a,b,c,d=self.coordinateList #souřadnice jednotlivých kostek
        if self.state==1:
            #jak se souřadnice změní, když je tvar otočí. v případě nejasností nakresli
            newCoordList=[a,(b[0]+1,b[1]-1),(c[0]+1,c[1]+1),(d[0]-1,d[1]+1)]
            temp=2 
        elif self.state==2:
            newCoordList=[a,(b[0]+1,b[1]+1),(c[0]-1,c[1]+1),(d[0]-1,d[1]-1)]
            temp=3
        elif self.state==3:
            newCoordList=[a,(b[0]-1,b[1]+1),(c[0]-1,c[1]-1),(d[0]+1,d[1]-1)]
            temp=4 
        else:
            newCoordList=[a,(b[0]-1,b[1]-1),(c[0]+1,c[1]-1),(d[0]+1,d[1]+1)]
            temp=1
        return newCoordList, temp




# funkce pro běh hry 
def startNewShape(root,canvas):
    """
    vytvoří náhodnou kostku, což odstartuje hru
    má funkce pro pohyb, spojené se šipkami
    když se nemůže pohnout dolů, vytvoří se nový
    """
    shape_number=random.randint(1,7)
    if shape_number==1:
        shape=square(root,canvas)
    elif shape_number==2:
        shape=Z(root,canvas)
    elif shape_number==3:
        shape=S(root,canvas)    
    elif shape_number==4:
        shape=reversedL(root,canvas)
    elif shape_number==5:
        shape=L(root,canvas)
    elif shape_number==6:
        shape=I(root,canvas)
    else:
        shape=triangle(root,canvas)
        
def updateScore(master,fullLines):
    """
    funkce pro zápis skóre 
    - na začátku hry 
    - po dopadnutí kostky, kdy se sečtou příp. odbouchlé řádky (full lines)
    dodělat: aby se hodila na herní obrazovku, ne jen do konzole
    """
    global points
    
    if fullLines==1:
        points+=1
    elif fullLines==2:
        points+=3
    elif fullLines==3:
        points+=5
    elif fullLines==4:
        points+=7
    else:
        return 0
    master.title("score: "+str(points))
         

# základní parametry okna s hrou    
s=25       #zvětšení. číslo, ktrým se přenásobují sorřadnice a rozměry
w,h=10,16 #šířka (x) a výška (y) hracího pole v rel. jednotkách
points=0
shape_count=0

forbidden_coordinates=[]
inactive_shapes=[]


# tvorba hracího pole
root=Tk()
root.title("score: "+str(points))
updateScore(root,0)

c=Canvas(root,width=w*s,height=h*s,bg="white")
c.pack()
# vyčtverečkování hracího pole
for n in range(w):
    for m in range(h):
        c.create_rectangle(n*s,m*s,(n+1)*s,(m+1)*s)

# spouštění hry
startNewShape(root,c)

root.mainloop()
