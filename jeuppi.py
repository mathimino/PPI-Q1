import math
import pygame
import sys
import random
import os

##### Constantes #####

NOIR = (0, 0, 0)
JAUNE = (255, 255, 0)
ROUGE = (255,0,0)
ORANGE = (255,165,0)
BLEU = (0,0,255)
WHITE = (255, 255, 255)

RAYON_VAISSEAU = 15
RAYON_PLANETE_MIN=50
RAYON_PLANETE_MAX=250
DIST_ENTRE_PLANETE = 300

LIMITES_JEU = [10000,10000]

RAYON_INFLUENCE = 1000
CONSTANTE_GRAV = 0.0002

#genereation carte
NBR_PLANETE_MIN = 750
NBR_PLANETE_MAX=1000

##### Fin constantes #####

# Paramètres

dimensions_fenetre = (1280, 1024)  # en pixels
images_par_seconde = 25

# Initialisation de variables

position_vaisseau = [dimensions_fenetre[0]/2,dimensions_fenetre[1]/2]
orientation_vaisseau = 0
cpt_propuls = 0

t_avant = 0
v_avant = [0,0]

vaisseau_avance = False
vaisseau_tourne_droite = False
vaisseau_tourne_gauche = False

# Initialisation

pygame.init()

fenetre = pygame.display.set_mode(dimensions_fenetre)
pygame.display.set_caption("ASTEROIDZ")
pygame.key.set_repeat(10, 10)

horloge = pygame.time.Clock()
couleur_fond = NOIR

scene = []

police = pygame.font.SysFont('monospace', dimensions_fenetre[1]//50, True)

# Création de listes contenant les images de leur répertoirs respectifs
planetes_images = []
for image_planete in os.listdir("images/planetes/"):
    planetes_images.append(pygame.image.load('images/planetes/' + image_planete).convert_alpha(fenetre))


vaisseau_images =[pygame.image.load('images/vaisseauettein.png').convert_alpha(fenetre),
                  pygame.image.load('images/vaisseauallume.png').convert_alpha(fenetre)]

# Fonctions

def gerer_touche(event):
    global vaisseau_avance
    global orientation_vaisseau
    global vaisseau_tourne_droite
    global vaisseau_tourne_gauche
   
    if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
        key = event.key
        match key:
            case pygame.K_q:
                if vaisseau_tourne_gauche == False and event.type == pygame.KEYDOWN:
                    vaisseau_tourne_gauche = True
                elif vaisseau_tourne_gauche and event.type == pygame.KEYUP:
                    vaisseau_tourne_gauche = False
            case pygame.K_d:
                if vaisseau_tourne_droite == False and event.type == pygame.KEYDOWN:
                    vaisseau_tourne_droite = True
                elif vaisseau_tourne_droite and event.type == pygame.KEYUP:
                    vaisseau_tourne_droite = False
            case pygame.K_z:
                #  Le vaisseau avance tant que la touche n'est pas lachée
                if vaisseau_avance == False and event.type == pygame.KEYDOWN:
                    vaisseau_avance = True
                elif vaisseau_avance and event.type == pygame.KEYUP:
                    vaisseau_avance = False
            case pygame.K_e:
                stop_vaisseau()

def afficher_vaisseau(position_vaisseau, orientation_vaisseau):
    if vaisseau_avance:  
        image_vaisseau = vaisseau_images[1]
        photo_vaisseau = pygame.transform.scale(image_vaisseau,(RAYON_VAISSEAU*2,RAYON_VAISSEAU*2))
        #Il faut rajouter un moins sinon l'image du vaisseau tourne dans le mauvais sens
        photo_vaisseau_r = pygame.transform.rotate(photo_vaisseau,-orientation_vaisseau)
        position_vaisseau_photo = pygame.Rect(position_vaisseau[0]-RAYON_VAISSEAU,position_vaisseau[1]-RAYON_VAISSEAU,2*RAYON_VAISSEAU,2*RAYON_VAISSEAU)
        fenetre.blit(photo_vaisseau_r,position_vaisseau_photo)
    else: 
        image_vaisseau = vaisseau_images[0]
        photo_vaisseau = pygame.transform.scale(image_vaisseau,(RAYON_VAISSEAU*2,RAYON_VAISSEAU*2))
        #Il faut rajouter un moins sinon l'image du vaisseau tourne dans le mauvais sens
        photo_vaisseau_r = pygame.transform.rotate(photo_vaisseau,-orientation_vaisseau)
        position_vaisseau_photo = pygame.Rect(position_vaisseau[0]-RAYON_VAISSEAU,position_vaisseau[1]-RAYON_VAISSEAU,2*RAYON_VAISSEAU,2*RAYON_VAISSEAU)
        fenetre.blit(photo_vaisseau_r,position_vaisseau_photo)      
    return 

# Dear Arthur, va te faire foutre avec ton code à la chat gpt ça m'a pris trois heures à débuguer

# Fonction qui calcule la différence entra l'ancienne et la nouvelle position du vaisseau (afin de l'appliquer aux élément du jeu)
def get_delta_pos(temps_maintenant,masse_vaisseau,force,orientation_vaisseau,stop=False):
    global t_avant
    global v_avant
    global position_vaisseau
    global scene
    
    #cordonnés du vaisseau dans la map
    x0,y0= position_vaisseau

    vx0, vy0 = v_avant
    if t_avant == 0:
        t_avant = temps_maintenant
    delta_t = temps_maintenant - t_avant

    #coordonnés du vaisseau dans le repere écran
    x_vaisseau = dimensions_fenetre[0]/2
    y_vaisseau = dimensions_fenetre[1]/2
    
    #accelereation moteur
    a = force/masse_vaisseau
    angle_rad = math.radians(orientation_vaisseau)
    ax = a*math.cos(angle_rad)
    ay = a*math.sin(angle_rad)
    
    # calcul gravité pour chaque planete
    a_planete = calcul_gravite_planete(x_vaisseau,y_vaisseau,masse_vaisseau)
    ax+=a_planete[0]
    ay+=a_planete[1]

    #mise a jour vitesse
    vx = vx0+ax*delta_t
    vy = vy0+ay*delta_t
    
    #mise a jour position du vaisseau
    x =x0 + vx0*delta_t + (ax*delta_t**2)/2
    y =y0 + vy0*delta_t + (ay*delta_t**2)/2

    #gestion des colisions du vaisseau avec la limite de la map
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
    
    # Nouvelle position du vaisseau dans la map
    position_vaisseau = [x,y]

    # On retourne la différence entre l'ancienne et nouvelle position du vaisseau
    return [x0-x,y0-y]

def calcul_gravite_planete(x_vaisseau,y_vaisseau,masse_vaisseau):
    a_planete_x = 0
    a_planete_y = 0
    for entite in scene : 
            if entite["type"]=="planete":
                x_planete,y_planete = entite["position"]

                #distance au carré entre le vaisseau et la planete choisie
                delta_x = x_planete-x_vaisseau
                delta_y = y_planete-y_vaisseau
                r2 = delta_x**2 + delta_y**2

                #on applique la gravité pour un rayon appartenant à [0,rayon_influence]
                if r2<= RAYON_INFLUENCE**2 and r2>0:
                    r = math.sqrt(r2)
                    masse_planete = entite["masse"]

                    #calcul gravité
                    Force_grav = CONSTANTE_GRAV*masse_planete*masse_vaisseau/r2
                    a_grav = Force_grav/masse_vaisseau
                    #on additionne la gravité à celle du moteur(+vecteur unitaire pour la direction)
                    a_planete_x+=a_grav*(delta_x/r)
                    a_planete_y+=a_grav*(delta_y/r)
    return a_planete_x,a_planete_y


def stop_vaisseau():
    get_delta_pos(pygame.time.get_ticks(),1,0,orientation_vaisseau,True)


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
    

def affiche(scene,delta_pos):
    for entite in scene:
        entite["position"][0] += delta_pos[0]
        entite["position"][1] += delta_pos[1]
        if entite["type"] == "planete":
            afficher_planete(entite)
    afficher_vaisseau([dimensions_fenetre[0]/2,dimensions_fenetre[1]/2],orientation_vaisseau)

    coord_txt= police.render("X:" + str(round(position_vaisseau[0])) + ",Y:" + str(round(position_vaisseau[1])), True, WHITE)
    fenetre.blit(coord_txt, (0,0))
    angle_txt= police.render("Angle:" + str(orientation_vaisseau,) + " deg", True, WHITE)
    fenetre.blit(angle_txt, (0,15))


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
generer_carte()

# Boucle de jeu
while True:
    for event in pygame.event.get():
        # print(evenement.type)
        gerer_touche(event)

    # Calcul du nouvel angle du vaisseau (modulo 360)
    if vaisseau_tourne_droite:
        orientation_vaisseau = (orientation_vaisseau + 5)%360
    if vaisseau_tourne_gauche:
        orientation_vaisseau = (orientation_vaisseau - 5)%360

    force = 0
    if vaisseau_avance:
        force = 0.0003
    else:
        force = 0

    fenetre.fill(couleur_fond)

    delta_pos = get_delta_pos(pygame.time.get_ticks(),1,force,orientation_vaisseau)

    affiche(scene, delta_pos)
    # collision_planete()
    pygame.display.flip()
    horloge.tick(images_par_seconde)
    