import math
import pygame
import sys
import random

# Constantes

# NOIR = (0, 0, 0)
# JAUNE = (255, 255, 0)
# ROUGE = (255,0,0)
# ORANGE = (255,165,0)
# BLEU = (0,0,255)
# WHITE = (255, 255, 255)

# LIMITES_JEU = [10000,10000]

RAYON_INFLUENCE = 1000
CONSTANTE_GRAV = 0.0002

#genereation carte
NBR_PLANETE_MIN = 750
NBR_PLANETE_MAX=1000
#intialisation images des planetes


# Paramètres

dimensions_fenetre = (1280, 1024)  # en pixels
images_par_seconde = 25

# Variables

position_vaisseau = [dimensions_fenetre[0]/2,dimensions_fenetre[1]/2]
orientation_vaisseau = 0
cpt_propuls = 0
RAYON_VAISSEAU = 15
RAYON_PLANETE_MIN=50
RAYON_PLANETE_MAX=250
DIST_ENTRE_PLANETE = 300




t_avant = 0
v_avant = [0,0]

# Initialisation

pygame.init()

fenetre = pygame.display.set_mode(dimensions_fenetre)
pygame.display.set_caption("ASTEROIDZ")
pygame.key.set_repeat(10, 10)

horloge = pygame.time.Clock()
couleur_fond = NOIR

scene = []

police = pygame.font.SysFont('monospace', dimensions_fenetre[1]//50, True)

planetes_images =[pygame.image.load('images/mars.png').convert_alpha(fenetre),
                  pygame.image.load('images/terre.png').convert_alpha(fenetre),
                  pygame.image.load('images/jupiter.png').convert_alpha(fenetre),
                  pygame.image.load('images/venus.png').convert_alpha(fenetre),
                  pygame.image.load('images/mercure.png').convert_alpha(fenetre),
                  pygame.image.load('images/uranus.png').convert_alpha(fenetre),
                  pygame.image.load('images/saturne.png').convert_alpha(fenetre),
                  pygame.image.load('images/neptune.png').convert_alpha(fenetre),
                  ]

vaisseau_images =[pygame.image.load('images/vaisseauettein.png').convert_alpha(fenetre),
                  pygame.image.load('images/vaisseauallume.png').convert_alpha(fenetre)]
# Fonctions

def gerer_touche(evenement):
    global cpt_propuls
    global orientation_vaisseau
    

    if evenement.type == pygame.KEYDOWN:
        key = evenement.key
        if key == pygame.K_q or key == pygame.K_LEFT:
            orientation_vaisseau = orientation_vaisseau - 9
        elif key == pygame.K_d or key == pygame.K_RIGHT:
            orientation_vaisseau = orientation_vaisseau + 9
        elif key == pygame.K_z or key == pygame.K_UP:
            cpt_propuls = 5
   
            

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
        
        image_vaisseau = vaisseau_images[1]
        photo_vaisseau = pygame.transform.scale(image_vaisseau,(RAYON_VAISSEAU*2,RAYON_VAISSEAU*2))
        photo_vaisseau_r = pygame.transform.rotate(photo_vaisseau,270+orientation_vaisseau)
        position_vaisseau_photo = pygame.Rect(position_vaisseau[0]-RAYON_VAISSEAU,position_vaisseau[1]-RAYON_VAISSEAU,2*RAYON_VAISSEAU,2*RAYON_VAISSEAU)
        fenetre.blit(photo_vaisseau_r,position_vaisseau_photo)
    else: 
        image_vaisseau = vaisseau_images[0]
        photo_vaisseau = pygame.transform.scale(image_vaisseau,(RAYON_VAISSEAU*2,RAYON_VAISSEAU*2))
        photo_vaisseau_r = pygame.transform.rotate(photo_vaisseau,270+orientation_vaisseau)
        position_vaisseau_photo = pygame.Rect(position_vaisseau[0]-RAYON_VAISSEAU,position_vaisseau[1]-RAYON_VAISSEAU,2*RAYON_VAISSEAU,2*RAYON_VAISSEAU)
        fenetre.blit(photo_vaisseau_r,position_vaisseau_photo)       
    
        

    
    return 




def mettre_a_jour_position(temps_maintenant,masse_vaisseau,force,orientation_vaisseau,stop=False):
    global t_avant
    global v_avant
    global position_vaisseau
    global scene
    
    #cordonné du vaisseau ,monde
    
    x0,y0= position_vaisseau
    vx0, vy0 = v_avant
    if t_avant == 0:
        t_avant = temps_maintenant
    delta_t = temps_maintenant - t_avant
#coordonné vaisseau dans le repere ecran
    x_vaisseau = dimensions_fenetre[0]/2
    y_vaisseau = dimensions_fenetre[1]/2
    
    #accelereation moteur
    a = force/masse_vaisseau
    ax = a*math.cos(orientation_vaisseau)
    ay = a*math.sin(orientation_vaisseau)
    
    #calcul gravité somme planete
    for entite in scene : 
        if entite["type"]=="planete":
            x_planete,y_planete = entite["position"]
            #distance entre le vaisseau et la planete choisie
            delta_x = x_planete-x_vaisseau
            delta_y = y_planete-y_vaisseau
            r2 = delta_x**2 + delta_y**2
            #on applique la gravité pour un rayon appartenant à [0,rayon_influence]
            if r2>0 and r2<= RAYON_INFLUENCE**2:
                r = math.sqrt(r2)
                masse_planete = entite["masse"]
                #calcul gravité
                Force_grav = CONSTANTE_GRAV*masse_planete*masse_vaisseau/r2
                a_grav = Force_grav/masse_vaisseau
                #on additionne la gravité à celle du moteur(+vecteur unitaire pour la direction)
                ax+=a_grav*(delta_x/r)
                ay+=a_grav*(delta_y/r)
    #mise a jour vitesse
    vx = vx0+ax*delta_t
    vy = vy0+ay*delta_t
    #mise a jour position(plutot decalage du monde)
    x =x0 + vx0*delta_t + (ax*delta_t**2)/2
    y =y0 + vy0*delta_t + (ay*delta_t**2)/2
    #gestion des colisions avec la limite de la map
    if abs(x) > abs(LIMITES_JEU[0]) or abs(y) > abs(LIMITES_JEU[1]) or stop:
        ax = 0
        ay = 0
        vx = 0
        vy = 0
        v_avant = [vx,vy]
        t_avant = temps_maintenant
        position_vaisseau = [x_vaisseau,y_vaisseau]
        return [0,0]
    
    v_avant = [vx,vy]
    t_avant = temps_maintenant
    
    position_vaisseau = [x,y]
    return [x0-x,y0-y]

def collision_planete():
    global scene
    x_vaisseau = dimensions_fenetre[0]/2
    y_vaisseau = dimensions_fenetre[1]/2

    for entite in scene:
        if entite["type"]== "planete":
            x_planete , y_planete = entite["position"]
            #distance entre la planete et le vaisseau
            x,y = position_vaisseau
            delta_x = x_planete-x_vaisseau
            delta_y = y_planete-y_vaisseau
            r2 = delta_x**2 + delta_y**2
            rayon_total = entite["rayon"]+RAYON_VAISSEAU
            if r2 <= rayon_total**2:
                pygame.quit()
                sys.exit()
    

def stop_vaisseau():
    mettre_a_jour_position(pygame.time.get_ticks(),1,0,orientation_vaisseau,True)


def affiche(scene):
    for entite in scene:
        entite["position"][0] += delta_pos[0]
        entite["position"][1] += delta_pos[1]
        if entite["type"] == "planete":
            afficher_planete(entite)
    afficher_vaisseau([dimensions_fenetre[0]/2,dimensions_fenetre[1]/2],orientation_vaisseau)

    coord_txt= police.render("X:" + str(round(position_vaisseau[0])) + ",Y:" + str(round(position_vaisseau[1])), True, WHITE)
    fenetre.blit(coord_txt, (0,0))





def ajouteEntite(scene, entite):
    scene.append(entite)

def nouvelle_planete(position,rayon,color,masse,photo):
    return {
        'type' : 'planete',
        'position' : position,
        'rayon' : rayon,
        'color' : color,
        'masse' : masse,
        'photo' : photo

    }

def afficher_planete(planete):
    photo_planete = planete['photo']
    position = pygame.Rect(planete['position'][0]-planete['rayon'],planete['position'][1]-planete['rayon'],2*planete['rayon'],2*planete['rayon'])
    fenetre.blit(photo_planete,position)
    return


def generer_carte():
    nb_planetes=random.randint(NBR_PLANETE_MIN,NBR_PLANETE_MAX)
    couleurs = [ROUGE,JAUNE,BLEU,ORANGE,WHITE]
    for planetes in range(nb_planetes):
        x_gen_planete = random.randint(-LIMITES_JEU[0],LIMITES_JEU[0])
        y_gen_planete = random.randint(-LIMITES_JEU[1],LIMITES_JEU[1])
        delta_x = x_gen_planete - position_vaisseau[0]
        delta_y = y_gen_planete -position_vaisseau[1]
        dist_spawn = delta_x**2 + delta_y**2

        if dist_spawn >= RAYON_INFLUENCE**2:
            rayon = random.randint(RAYON_PLANETE_MIN,RAYON_PLANETE_MAX)
            masse = rayon*rayon*3
            couleur_planete = random.choice(couleurs)
            choix_images_planete = random.choice(planetes_images)
            photo_planete=pygame.transform.scale(choix_images_planete,(rayon*2,rayon*2))
            peut_placer=True
            for planetes_cree in scene : 
                if planetes_cree["type"]== "planete":
                    x_planete,y_planete = planetes_cree["position"]
                    delta_xp = x_gen_planete-x_planete
                    delta_yp = y_gen_planete-y_planete
                    dist_planete2 = delta_xp**2 + delta_yp**2
                    distance_min = rayon + planetes_cree["rayon"]+DIST_ENTRE_PLANETE
                    if dist_planete2 <distance_min**2:
                        peut_placer = False
            if peut_placer:
                planete = nouvelle_planete([x_gen_planete,y_gen_planete],rayon,couleur_planete,masse,photo_planete)
                ajouteEntite(scene,planete)
###
generer_carte()
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

    delta_pos = mettre_a_jour_position(pygame.time.get_ticks(),1,force,orientation_vaisseau)

    affiche(scene)
    collision_planete()
    
    
    pygame.display.flip()
    horloge.tick(images_par_seconde)
    