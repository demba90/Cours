# -*- coding: utf-8 -*-
""" classe Maillage elements finis 2D """
from numpy import *
import matplotlib.pyplot as plt
import matplotlib.tri as tri
# calcul de l'abscisse curviligne S des pts d'une courbe X
def Curvil(X):
    n=X.shape[0]
    dX=X[1:n,:]-X[0:n-1,:]
    L=sum(sqrt(dX[:,0]*dX[:,0] + dX[:,1]*dX[:,1]));
    S=zeros((n));
    S[1:n]=sqrt(dX[:,0]*dX[:,0]+dX[:,1]*dX[:,1])/L;
    return S.cumsum()
# calcul de la position x,y d'un point d'abscisse s sur la courbe X d'abscisse S
def XYCurv(X,S,s):
    n=X.shape[0]
    i=0
    while (i<n) and (s>S[i]):
     i=i+1
    # le pts est entre les noeuds i-1 et i
    ds=(S[i]-s)/(S[i]-S[i-1]);
    xy=X[i,:]+ds*(X[i-1,:]-X[i,:]);
    return xy
# transformation
class transform(object):
    def __init__(self,A1,A2,A3,A4):
        self.A1=A1
        self.A2=A2
        self.A3=A3
        self.A4=A4
        return
    # transformation conforme
    def FChap(self,u,v):
        xy=(1-v)*self.F1+u*self.F2+v*self.F3+(1-u)*self.F4;
        xy=xy+(u-1)*(1-v)*self.A1+(v-1)*u*self.A2-u*v*self.A3+(u-1)*v*self.A4;
        return xy
#
# maillage
# ========
class Maillage(object):
    """ maillage EF avec numérotation a partir de 0 """
    def __init__(self,nom,nn=0,ne=0,gtype=1):
        self.nom=nom
        self.nn=nn
        self.ne=ne
        self.gtype=1                # type triangle ou quadrangle (1=P1, 2=Q1, 3=P2, 4=Q2)
        self.ddl=[3,4,6,8][gtype-1] # nbre de ddl / elt
        self.X = zeros((nn,2))                     # coordonnees
        self.Tbc = zeros((ne,self.ddl),dtype=int)  # table de connection
        self.Frt = zeros((nn),dtype=int)           # frontiere si #0
        self.Reg = ones((ne),dtype=int)            # region
        return

    def info(self):
        print self.nom
        print "ne=",self.ne," nn=",self.nn," type=",self.gtype," ddl=",self.ddl
        print "Xmin/max Ymin/max=",amin(self.X[:,0]),amax(self.X[:,0]),amin(self.X[:,1]),amax(self.X[:,1])
        # calcul surface
        surf=0.0
        for l in range(self.ne):
            surf=surf+self.aire(l)
        print "Surface ",surf
        return

    def aire(self,l):
        """ calcul de l'aire de l'elemet l"""
        n=self.Tbc[l,:]
        S21=self.X[n[0],:]-self.X[n[1],:]
        S13=self.X[n[2],:]-self.X[n[0],:]
        surf = 0.5*(S13[0]*S21[1]-S13[1]*S21[0])
        return surf

    def quadrangle(self,L,n1,n2,num=[1,2,3,4],gtype=1,ttype=0):
        """ genere un maillage d'un quadrangle """
        X1=zeros((n1,2))
        X1[:,0]=linspace(L[0][0],L[1][0],n1)
        X1[:,1]=linspace(L[0][1],L[1][1],n1)
        X2=zeros((n2,2))
        X2[:,0]=linspace(L[1][0],L[2][0],n2)
        X2[:,1]=linspace(L[1][1],L[2][1],n2)
        X3=zeros((n1,2))
        X3[:,0]=linspace(L[2][0],L[3][0],n1)
        X3[:,1]=linspace(L[2][1],L[3][1],n1)
        X4=zeros((n2,2))
        X4[:,0]=linspace(L[3][0],L[0][0],n2)
        X4[:,1]=linspace(L[3][1],L[0][1],n2)
        Quacou(self,X1,X2,X3,X4,num,Gtype=gtype,Ttype=ttype)
        return

    def plotmesh(self):
        """ affiche le maillage """
        for  l in range(self.ne):
            num=zeros((4),dtype=int)
            num[0:3]=self.Tbc[l,:]; num[3]=self.Tbc[l,0]
            plt.plot(self.X[ix_(num,[0])],self.X[ix_(num,[1])],'k-')
        return

    def plotfront(self):
        """ trace frontiere """
        COL=('k','b', 'g', 'r', 'c', 'm', 'y')
        ARF=self.arfront()
        for L in ARF:
                plt.plot(self.X[L,0],self.X[L,1],lw=2,color='k')
                code=self.Frt[L[0]]
                col="#777700"
                if code<7: col=COL[code]
                plt.plot(self.X[L[0],0],self.X[L[0],1],'o',color=col)
                code=self.Frt[L[1]]
                col="#777700"
                if code<7: col=COL[code]
                plt.plot(self.X[L[1],0],self.X[L[1],1],'o',color=col)
        return

    def plotelt(self):
        """ trace numero des elts """
        for k in range(self.ne):
            num=self.Tbc[k,:]
            S = self.X[ix_(num,[0,1])]
            G = sum(S,axis=0)/3.
            plt.text(G[0],G[1],"%d"%k,bbox=dict(facecolor='green', alpha=0.5))
        return

    def plotnds(self):
        """ trace numeo des noeuds"""
        for i in range(self.nn):
            plt.text(self.X[i,0],self.X[i,1],"%d"%i,bbox=dict(facecolor='red', alpha=0.5))
        return

    def aretes(self):
        """ liste des aretes du maillage """
        # liste des aretes (en double)
        LA=vstack((self.Tbc[:,0:2],self.Tbc[:,1:],transpose(vstack((self.Tbc[:,2],self.Tbc[:,0])))))
        LA=sort(LA)
        # elimination des doubles par conversion en chaine des lignes
        # puis utilisation de unique et conversion en entier
        dim=LA.itemsize
        AR=unique(LA.view('S%d'%(2*dim))).view ('i%d'%dim)
        return AR.reshape((len(AR)/2, 2))

    # calcul des aretes frontieres (attention non orientées)
    def arfront(self):
        """ liste des aretes frontieres """
        # liste des artes (en double)
        LA=vstack((self.Tbc[:,0:2],self.Tbc[:,1:],transpose(vstack((self.Tbc[:,2],self.Tbc[:,0])))))
        LA=sort(LA)
        dim=LA.itemsize
        AR=unique(LA.view('S%d'%(2*dim))).view ('i%d'%dim)
        AR=AR.reshape((len(AR)/2, 2))
        # boucle sur les aretes de G
        narf=0
        for L in AR:
           if self.Frt[L[0]]!=0 and self.Frt[L[1]]!=0 :
                # verification si arete frontiere
                I1=where(LA[:,0]==L[0])[0]
                I2=where(LA[ix_(I1)]==L[1])[1]
                if len(I2)==1:
                    AR[narf,:]=L
                    narf+=1
        return AR[:narf,:]

    def gradient(self,l):
        """ calcul le gradient des fonctions de forme de l'elt l et l'aire"""
        p=zeros((5),dtype=int)
        n=self.Tbc[l,:]; # numero des sommets de 0 a nn-1
        p[0:3]=n[:]; p[3:5]=n[0:2]; # permutation circulaire
        dX=self.X[ix_(p[1:4],[0,1])]-self.X[ix_(p[2:5],[0,1])]; # aretes
        Aire=0.5*(dX[0,0]*dX[1,1]-dX[1,0]*dX[0,1]);
        dN=array([dX[:,1],-dX[:,0]])/(2*Aire);
        return dN,Aire

    # tracer champ Z sur maillage
    def isosurf(self,Z,titre,front=True):
        """ trace isosurface de Z sur le maillage G"""
        triang=tri.Triangulation(self.X[:,0],self.X[:,1],triangles=self.Tbc)
        plt.tricontourf(triang, Z)
        if front:
            ARF=self.arfront()
            for L in ARF:
                plt.plot(self.X[L,0],self.X[L,1],lw=2,color='k')
        plt.colorbar()
        plt.title(titre)
        return

    # raffinement maillage
    def raffine(self):
        """raffinement maillage"""
        AR=self.aretes()
        nar=AR.shape[0]
        G2=Maillage(self.nom+" x2")
        G2.nn=self.nn+nar
        # creation des nds / artes
        G2.X=zeros((G2.nn,2),dtype=float)
        G2.X[:self.nn,:]=self.X[:,:]
        G2.Frt=zeros((G2.nn),dtype=int)
        G2.Frt[:self.nn]=self.Frt[:]
        nn2=self.nn
        for L in AR:
            G2.X[nn2,:]=0.5*(self.X[L[0],:]+self.X[L[1],:])
            nn2 += 1
        # aretes frontieres
        ARF=self.arfront()
        for L in ARF:
            I1=where(AR[:,0]==L[0])[0]
            I2=where(AR[ix_(I1),1]==L[1])[1]
            nn2=self.nn+I1[I2[0]]
            G2.Frt[nn2]=max(self.Frt[L[0]],self.Frt[L[1]])
        # creation des triangles
        G2.ne=4*self.ne
        G2.Tbc=zeros((G2.ne,3),dtype=int)
        N=zeros((6),dtype=int)
        for k in range(self.ne):
            N[:3]=self.Tbc[k,:]
            # recherche des nouveaux noeuds
            L1=[N[1],N[2]];
            if N[1]>N[2]: L1=[N[2],N[1]];
            I1=where(AR[:,0]==L1[0])[0]
            I2=where(AR[ix_(I1),1]==L1[1])[1]
            N[3]=self.nn+I1[I2[0]]
            L1=[N[2],N[0]];
            if N[2]>N[0]: L1=[N[0],N[2]];
            I1=where(AR[:,0]==L1[0])[0]
            I2=where(AR[ix_(I1),1]==L1[1])[1]
            N[4]=self.nn+I1[I2[0]]
            L1=[N[0],N[1]];
            if N[0]>N[1]: L1=[N[1],N[0]];
            I1=where(AR[:,0]==L1[0])[0]
            I2=where(AR[ix_(I1),1]==L1[1])[1]
            N[5]=self.nn+I1[I2[0]]
            # creation des 4 triangles
            G2.Tbc[4*k  ,:]=[N[0],N[5],N[4]]
            G2.Tbc[4*k+1,:]=[N[1],N[3],N[5]]
            G2.Tbc[4*k+2,:]=[N[2],N[4],N[3]]
            G2.Tbc[4*k+3,:]=[N[3],N[4],N[5]]
        # fin
        return G2

    def interp(self,f):
        """ interpole une fonction f(x,y) sur le maillage"""
        F=zeros(self.nn)
        for i in range(self.nn):
            F[i]=f(self.X[i,0],self.X[i,1])
        return F
#
# generation maillage EF par transformation Quadrilatere courbes
# ==============================================================
def Quacou(G,X1,X2,X3,X4,num=None,Gtype=1,Ttype=0):
    """
        generation d'un maillage par transformation
        X1,X2,X3,X4 coordonnees (x,y) des cotes du maillage
        num   = numerotation des frontieres (optionnel)
        Gtype = generation d'un maillage triangle =1 ou quadrangle=2 (optionnel)
        Ttype = type de triangle (decoupage quadrangle) 0 automatique, 1 triangle regulier, 2 triangle alterne
    """
    n1 = X1.shape[0]
    n2 = X2.shape[0]
    if (n1 != X3.shape[0]) or (n2 != X4.shape[0]) :
        print "erreur dimension dans Quacou"
        return
    NUM=[1,2,3,4]  # numerotation des frontieres par defaut
    if num!=None : NUM=num
    # initialisation geometrie
    if Gtype==1 :
        G.__init__(G.nom,n1*n2,(n1-1)*(n2-1)*2,1)
    else :
        G.__init__(G.nom,n1*n2,(n1-1)*(n2-1)  ,2)
    # calcul des abscisses curvilignes
    S1=Curvil(X1); S2=Curvil(X2);
    S3=Curvil(X3); S4=Curvil(X4);
    # calcul de la transformation (coordonnees des 4 pts)
    trans = transform(X1[0,:],X2[0,:],X3[0,:],X4[0,:])
    n=0;
    for j in range(n2):
        s2=S2[j]; s4=1-S4[n2-j-1];
        for i in range(n1):
            s1=S1[i]; s3=1-S3[n1-i-1];
            # coordonnees dans le carre unite du nouveau nds n
            d1=1-(s3-s1)*(s2-s4)
            u=(s1+s4*(s3-s1))/d1
            v=(s4+s1*(s2-s4))/d1
            trans.F1=XYCurv(X1,S1,u)
            trans.F2=XYCurv(X2,S2,v)
            trans.F3=XYCurv(X3,S3,1-u)
            trans.F4=XYCurv(X4,S4,1-v)
            G.X[n,:]=trans.FChap(u,v)
            n=n+1;
    # creation des elts triangles
    if (Gtype !=2 ) :
        l=0; t1230 = False;
        for j in range(1,n2):
            t123  = t1230
            t1230 =not t1230
            for i in range(1,n1):
                i1=(j-1)*n1+i-1;
                i2=i1+1;
                i3=j*n1+i;
                i4=i3-1;
                if (Ttype==1):
                    t123= True
                elif (Ttype==2):
                    t123= not t123;
                else :
                # comparaison des angles 123 et 234
                    dX23=G.X[i3,:]-G.X[i2,:]
                    dX21=G.X[i1,:]-G.X[i2,:]
                    cos123=dot(dX23,dX21)/linalg.norm(dX21)
                    dX34=G.X[i4,:]-G.X[i3,:]
                    cos234=dot(dX23,dX34)/linalg.norm(dX34)
                    t123=(cos123>=cos234);
                # genere les 2 trianfgles
                if (t123) :
                    G.Tbc[l,:]=[i1,i2,i3]
                    l=l+1
                    G.Tbc[l,:]=[i4,i1,i3]
                    l=l+1
                else :
                    G.Tbc[l,:]=[i1,i2,i4]
                    l=l+1
                    G.Tbc[l,:]=[i4,i2,i3]
                    l=l+1
    # creation quadrangle
    else:
        l=0
        for j in range(n2-1):
            for i in range(n1-1):
                i1=(j-1)*n1+i;
                i2=i1+1;
                i3=j*n1+i+1;
                i4=i3-1;
                G.Tbc[l,:]=[i1,i2,i3,i4];
                l=l+1;
    # frontiere  ( numerotation n=(j-1)*n1+i )
    G.Frt[0:n1]=NUM[0];
    G.Frt[(n2-1)*n1:n2*n1]=NUM[2]
    G.Frt[n1-1:n2*n1:n1]=NUM[1]
    G.Frt[0   :n2*n1:n1]=NUM[3]
    # region initialise a 1 par defaut
    # G.Reg=ones(G.ne)
    return;
#
# test
if __name__ == "__main__":
    G=Maillage("Maillage Test")
    G.quadrangle([[0.,0.],[1.,0.],[1.,1.],[0.,1.]],3,3)
    G=G.raffine()
    G.info()
    plt.figure()
    G.plotmesh()
    G.plotfront()
    G.plotelt()
    G.plotnds()
    plt.show()
