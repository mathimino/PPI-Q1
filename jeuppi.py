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

RAYON_VAISSEAU = 20
RAYON_PLANETE_MIN=100
RAYON_PLANETE_MAX=300
DIST_MIN_ENTRE_PLANETE = 300

LIMITES_JEU = [10000,10000]

RAYON_INFLUENCE = 1000
CONSTANTE_GRAV = 0.0001

#genereation carte
NBR_PLANETE_MIN = 750
NBR_PLANETE_MAX=1000

##### Fin constantes #####

# Paramètres

dimensions_fenetre = (900,900)  # en pixels
images_par_seconde = 25

# Initialisation de variables

# Vaisseau
position_vaisseau = [dimensions_fenetre[0]/2,dimensions_fenetre[1]/2]
#coordonnés du vaisseau dans le repere écran
x_vaisseau_ecran,y_vaisseau_ecran = dimensions_fenetre[0]/2,dimensions_fenetre[1]/2
orientation_vaisseau = 0
puissance_vaisseau = 1
masse_vaisseau = 3000
vitesse_max = 1
force_freinage = -0.5
vx = 0
vy = 0
ax = 0
ay = 0

t_avant = 0
v_avant = [0,0]

vaisseau_avance = False

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


    if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
        key = event.key
        match key:
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
def get_delta_pos(temps_maintenant,force_vaisseau,orientation_vaisseau,stop=False):
    global t_avant
    global v_avant
    global position_vaisseau
    global vx,vy,ax,ay
    global scene
    
    #cordonnés du vaisseau dans la map
    x0,y0= position_vaisseau

    vx0, vy0 = v_avant
    if t_avant == 0:
        t_avant = temps_maintenant
    delta_t = temps_maintenant - t_avant
    
    
    angle_rad = math.radians(orientation_vaisseau)
    #récupération de l'accélération du vaisseau
    a = force_vaisseau/masse_vaisseau
    ax = a*math.cos(angle_rad)
    ay = a*math.sin(angle_rad)
            

    # calcul gravité pour chaque planete
    a_planete = calcul_gravite_planete()
    ax+=a_planete[0]
    ay+=a_planete[1]

    #mise a jour vitesse
    vx = vx0+ax*delta_t
    vy = vy0+ay*delta_t

    # Vitesse max
    if abs(vx)>vitesse_max:
        if vx > 0:
            vx = vitesse_max
        else:
            vx = -vitesse_max
        ax = 0
    if abs(vy)>vitesse_max:
        if vy > 0:
            vy = vitesse_max
        else:
            vy = -vitesse_max
        ay = 0


    #mise a jour position du vaisseau
    x =x0 + vx0*delta_t + (ax*delta_t**2)/2
    y =y0 + vy0*delta_t + (ay*delta_t**2)/2

    #gestion des colisions du vaisseau avec la limite de la map
    if abs(x) > abs(LIMITES_JEU[0]) or abs(y) > abs(LIMITES_JEU[1]) or stop:
        vx = 0
        vy = 0
        v_avant = [vx,vy]
        t_avant = temps_maintenant
        position_vaisseau = [x0,y0]
        return [0,0]
    
    v_avant = [vx,vy]
    t_avant = temps_maintenant
    
    # Nouvelle position du vaisseau dans la map
    position_vaisseau = [x,y]

    # On retourne la différence entre l'ancienne et nouvelle position du vaisseau
    return [x0-x,y0-y]

def calcul_gravite_planete():
    a_planete_x = 0
    a_planete_y = 0
    for entite in scene : 
            if entite["type"]=="planete":
                x_planete,y_planete = entite["position"]

                #distance au carré entre le vaisseau et la planete choisie
                delta_x = x_planete-x_vaisseau_ecran
                delta_y = y_planete-y_vaisseau_ecran
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
    get_delta_pos(pygame.time.get_ticks(),0,orientation_vaisseau,True)


def collision_planete():
    global scene

    for entite in scene:
        if entite["type"]== "planete":
            x_planete , y_planete = entite["position"]
            #distance entre la planete et le vaisseau
            x,y = position_vaisseau
            delta_x = x_planete-x_vaisseau_ecran
            delta_y = y_planete-y_vaisseau_ecran
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
    angle_txt= police.render("Angle:" + str(round(orientation_vaisseau,2)) + " deg", True, WHITE)
    fenetre.blit(angle_txt, (0,15))
    ax_txt= police.render("Acceleration X:" + str(ax), True, WHITE)
    fenetre.blit(ax_txt, (0,30))
    vx_txt= police.render("Vitesse X:" + str(round(vx,2)), True, WHITE)
    fenetre.blit(vx_txt, (0,45))
    vy_txt= police.render("Vitesse Y:" + str(round(vy,2)), True, WHITE)
    fenetre.blit(vy_txt, (0,60))


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
    # Choix du nbr de planetes à créer
    nb_planetes=random.randint(NBR_PLANETE_MIN,NBR_PLANETE_MAX)
    couleurs = [ROUGE,JAUNE,BLEU,ORANGE,WHITE]
    for planetes in range(nb_planetes):
        # Génération de la position du la nouvelle planete
        x_gen_planete = random.randint(-LIMITES_JEU[0],LIMITES_JEU[0])
        y_gen_planete = random.randint(-LIMITES_JEU[1],LIMITES_JEU[1])
        delta_x = x_gen_planete - position_vaisseau[0]
        delta_y = y_gen_planete -position_vaisseau[1]
        dist_spawn2 = delta_x**2 + delta_y**2
        rayon = random.randint(RAYON_PLANETE_MIN,RAYON_PLANETE_MAX)
        
        #Si la nouvelle planete est au moins à une certaine distance du spawn du vaisseau
        if dist_spawn2 >= (rayon+(dimensions_fenetre[0]+dimensions_fenetre[1])/4)**2:
            masse = rayon*rayon*3
            couleur_planete = random.choice(couleurs)
            choix_images_planete = random.choice(planetes_images)
            photo_planete=pygame.transform.scale(choix_images_planete,(rayon*2,rayon*2))
            peut_placer=True
            
            #On vérifie que la nouvelle planete n'est pas trop proche des planetes déjà existantes
            for planetes_cree in scene : 
                if planetes_cree["type"]== "planete":
                    x_planete,y_planete = planetes_cree["position"]
                    delta_xp = x_gen_planete-x_planete
                    delta_yp = y_gen_planete-y_planete
                    dist_planetes2 = delta_xp**2 + delta_yp**2
                    distance_min = rayon + planetes_cree["rayon"]+DIST_MIN_ENTRE_PLANETE
                    if dist_planetes2 <distance_min**2:
                        peut_placer = False
            if peut_placer:
                planete = nouvelle_planete([x_gen_planete,y_gen_planete],rayon,couleur_planete,masse,photo_planete)
                ajouteEntite(scene,planete)


### Boucle de jeu ###

generer_carte()

while True:
    for event in pygame.event.get():
        gerer_touche(event)


    mouse_x,mouse_y = pygame.mouse.get_pos()
    delta_mouse_x, delta_mouse_y = mouse_x-x_vaisseau_ecran, mouse_y-y_vaisseau_ecran

    # Calcul du nouvel angle du vaisseau par rapport à la position de la souris (modulo 360)
    angle_rad = math.atan2(delta_mouse_y,delta_mouse_x)
    orientation_vaisseau = (math.degrees(angle_rad))%360

    if vaisseau_avance:
        force_vaisseau = puissance_vaisseau
    else:
        force_vaisseau = 0
    # force_vaisseau=puissance_vaisseau

    fenetre.fill(couleur_fond)

    delta_pos = get_delta_pos(pygame.time.get_ticks(),force_vaisseau,orientation_vaisseau)

    affiche(scene, delta_pos)
    # collision_planete()
    pygame.display.flip()
    horloge.tick(images_par_seconde)
    