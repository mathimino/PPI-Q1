import math
import pygame
import sys

# Constantes

NOIR = (0, 0, 0)
JAUNE = (255, 255, 0)
ROUGE = (255,0,0)
ORANGE = (255,165,0)
BLEU = (0,0,255)
WHITE = (255, 255, 255)

LIMITES_JEU = [1000,1000]

# Paramètres

dimensions_fenetre = (900, 800)  # en pixels
images_par_seconde = 25

# Variables

position_vaisseau = [0,0]
orientation_vaisseau = 0
cpt_propuls = 0

position_planete = [0,0]
planete_est_presente = False 
rayon_planete = 100

t_avant = 0
v_avant = [0,0]

# Initialisation

pygame.init()

fenetre = pygame.display.set_mode(dimensions_fenetre)
pygame.display.set_caption("Programme 7")
pygame.key.set_repeat(10, 10)

horloge = pygame.time.Clock()
couleur_fond = NOIR

scene = []

police = pygame.font.SysFont('monospace', dimensions_fenetre[1]//50, True)


# Fonctions

def gerer_touche(evenement):
    global cpt_propuls
    global orientation_vaisseau
    global position_planete
    global planete_est_presente

    if evenement.type == pygame.KEYDOWN:
        key = evenement.key
        if key == pygame.K_q or key == pygame.K_LEFT:
            orientation_vaisseau = orientation_vaisseau - 5*math.pi/20
        elif key == pygame.K_d or key == pygame.K_RIGHT:
            orientation_vaisseau = orientation_vaisseau + 5*math.pi/20
        elif key == pygame.K_z or key == pygame.K_UP:
            cpt_propuls = 5
    elif evenement.type == pygame.MOUSEBUTTONDOWN:
        if evenement.button == 1:
            position_planete = [evenement.pos[0],evenement.pos[1]]
            # planete_est_presente = True
        elif evenement.button == 3:
            planete_est_presente = False
            

def dessiner_triangle(couleur, p, r, a, b):
    x_p0, y_p0 = p

    x_p1 = x_p0 + r*math.cos(a+b) 
    y_p1 = y_p0 + r*math.sin(a+b) 
    
    x_p2 = x_p0 + r*math.cos(a-b) 
    y_p2 = y_p0 + r*math.sin(a-b) 

    pygame.draw.polygon(fenetre,couleur,[(x_p0,y_p0),(x_p1,y_p1),(x_p2,y_p2)])
    return

def afficher_vaisseau(position_vaisseau, orientation_vaisseau):
    if cpt_propuls > 0:
        dessiner_triangle(ORANGE,position_vaisseau,38,orientation_vaisseau+21*math.pi/20,math.pi/30)
        dessiner_triangle(ORANGE,position_vaisseau,38,orientation_vaisseau+19*math.pi/20,math.pi/30)
    dessiner_triangle(JAUNE,position_vaisseau,23,orientation_vaisseau+math.pi,math.pi/7)
    pygame.draw.circle(fenetre,ROUGE,position_vaisseau,15)
    return    

def mettre_a_jour_position(temps_maintenant,masse_vaisseau,force,orientation_vaisseau,masse_planete,position_planete,stop=False):
    global t_avant
    global v_avant
    global position_vaisseau
    

    x0, y0 = position_vaisseau
    vx0, vy0 = v_avant

    delta_t = temps_maintenant-t_avant

    a = force/masse_vaisseau
    ax = a*math.cos(orientation_vaisseau)
    ay = a*math.sin(orientation_vaisseau)


    if planete_est_presente:
        xp,yp = position_planete
        delta_xp = xp-x0
        delta_yp = yp-y0
        
        #distance planette-vaisseau au carré
        r2=(xp-x0)**2+(yp-y0)**2
        if r2 > 0:
            r=math.sqrt(r2)

            fg=0.001*masse_planete*masse_vaisseau/r2
            a_grav = fg/masse_vaisseau

            #acceleration*vecteur unitaire pour la composante (pour avoir la direction)
            ax+=a_grav*delta_xp/r
            ay+=a_grav*delta_yp/r

    vx= vx0 + ax*delta_t
    vy= vy0 + ay*delta_t

    #Coordonnées du vaisseau dans le plan
    x = x0 + vx0*delta_t + (ax*delta_t**2)/2
    y = y0 + vy0*delta_t + (ay*delta_t**2)/2
    

    #gestion des colisions avec la limite de la map
    if abs(x) > abs(LIMITES_JEU[0]) or abs(y) > abs(LIMITES_JEU[1]) or stop:
        ax = 0
        ay = 0
        vx = 0
        vy = 0
        v_avant = [vx,vy]
        t_avant = temps_maintenant
        position_vaisseau = [x0,y0]
        return [0,0]
    
    v_avant = [vx,vy]
    t_avant = temps_maintenant
    
    position_vaisseau = [x,y]
    return [x0-x, y0-y]

def stop_vaisseau():
    mettre_a_jour_position(pygame.time.get_ticks(),1,1,1,1,[0,0],True)


def affiche(scene):
    for entite in scene:
        entite["position"][0] += delta_pos[0]
        entite["position"][1] += delta_pos[1]
        if entite["type"] == "planete":
            afficher_planete(entite)
    afficher_vaisseau([dimensions_fenetre[0]/2,dimensions_fenetre[1]/2],orientation_vaisseau)

    coord_txt= police.render("X:" + str(round(position_vaisseau[0])) + ",Y:" + str(round(position_vaisseau[1])), True, WHITE)
    fenetre.blit(coord_txt, (0,0))


def colision_planete(position_planete,position_vaisseau):
    xp,yp=position_planete
    xv,yv=position_vaisseau
    r2=(xp-xv)**2+(yp-yv)**2
    if(r2<rayon_planete**2):
        pygame.quit()
        sys.exit()
    return


def ajouteEntite(scene, entite):
    scene.append(entite)

def nouvelle_planete(position,rayon,color):
    return {
        'type' : 'planete',
        'position' : position,
        'rayon' : rayon,
        'color' : color
    }

def afficher_planete(planete):
    pygame.draw.circle(fenetre,planete["color"],planete["position"],planete["rayon"])
    return


planete1= nouvelle_planete([0,0],50,ROUGE)
ajouteEntite(scene,planete1)

planete2= nouvelle_planete([700,700],150,JAUNE)
ajouteEntite(scene,planete2)

###

while True:
    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evenement.type == pygame.KEYDOWN or pygame.MOUSEBUTTONDOWN:
            gerer_touche(evenement)

    force = 0
    if cpt_propuls > 0:
        cpt_propuls = cpt_propuls -1
        force = 0.0003
    else:
        force = 0

    fenetre.fill(couleur_fond)

    delta_pos = mettre_a_jour_position(pygame.time.get_ticks(),1,force,orientation_vaisseau,1600,position_planete)

    affiche(scene)

    
    # if planete_est_presente:
    #     colision_planete(position_planete,position_vaisseau) 
    pygame.display.flip()
    horloge.tick(images_par_seconde)
    # print(round(position_vaisseau[0],0),round(position_vaisseau[1],0))