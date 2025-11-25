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
NOMBRE_ETOILES = 10000


##### Fin constantes #####

# Paramètres

dimensions_fenetre = (900,900)  # en pixels
images_par_seconde = 25

# Initialisation de variables
###optimisation
DISTANCE_AFFICHAGE = 3*dimensions_fenetre[0]
# Vaisseau
position_vaisseau = [dimensions_fenetre[0]/2,dimensions_fenetre[1]/2]
#coordonnés du vaisseau dans le repere écran
x_vaisseau_ecran,y_vaisseau_ecran = dimensions_fenetre[0]/2,dimensions_fenetre[1]/2
orientation_vaisseau = 0
puissance_vaisseau = 1
masse_vaisseau = 3000
vitesse_max = 1
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

scene = {
    "etoiles":[],
    "planetes" : [],
    "entites" : [],
    "vaisseau":[]
}

police = pygame.font.SysFont('monospace', dimensions_fenetre[1]//50, True)

# Création de listes contenant les images de leur répertoirs respectifs
planetes_images = []
for image_planete in os.listdir("images/planetes/"):
    planetes_images.append(pygame.image.load('images/planetes/' + image_planete).convert_alpha(fenetre))


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
                if event.type == pygame.KEYDOWN:
                    vaisseau_avance = allume_moteur(vaisseau_avance)    
                elif event.type == pygame.KEYUP:
                    vaisseau_avance = eteint_moteur(vaisseau_avance)
            case pygame.K_e:
                stop_vaisseau()

# Fonction qui calcule la différence entra l'ancienne et la nouvelle position du vaisseau (afin de l'appliquer aux élément du jeu)
def get_delta_pos(entite,temps_maintenant,force_entite,orientation_vaisseau,stop=False):
    global t_avant
    global v_avant
    global position_vaisseau
    
    #cordonnés du vaisseau dans la map
    x0,y0= position_vaisseau

    vx0, vy0 = entite["vitesse_x_avant"], entite["vitesse_y_avant"]
    if t_avant == 0:
        t_avant = temps_maintenant
    delta_t = temps_maintenant - entite["temps_avant"]
    
    
    angle_rad = math.radians(orientation_vaisseau)
    #récupération de l'accélération du vaisseau
    a = force_entite/entite["masse"]
    ax = a*math.cos(angle_rad)
    ay = a*math.sin(angle_rad)
            

    # calcul gravité pour chaque planete
    a_planete = calcul_gravite_planete(entite["masse"])
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
        entite["vitesse_x_avant"],entite["vitesse_y_avant"] = vx,vy
        entite["temps_avant"] = temps_maintenant
        position_vaisseau = [x0,y0]
        return [0,0]
    

    entite["vitesse_x_avant"],entite["vitesse_y_avant"] = vx,vy
    entite["vitesse_x"],entite["vitesse_y"] = vx,vy
    
    entite["temps_avant"] = temps_maintenant
    
    # Nouvelle position du vaisseau dans la map
    position_vaisseau = [x,y]

    # On retourne la différence entre l'ancienne et nouvelle position du vaisseau
    return [x0-x,y0-y]

def calcul_gravite_planete(masse_entite):
    a_planete_x = 0
    a_planete_y = 0
    for planete in scene['planetes']: 
                x_planete,y_planete = planete["position"]

                #distance au carré entre le vaisseau et la planete choisie
                delta_x = x_planete-x_vaisseau_ecran
                delta_y = y_planete-y_vaisseau_ecran
                r2 = delta_x**2 + delta_y**2

                #on applique la gravité pour un rayon appartenant à [0,rayon_influence]
                if r2<= RAYON_INFLUENCE**2 and r2>0:
                    r = math.sqrt(r2)
                    masse_planete = planete["masse"]

                    #calcul gravité
                    Force_grav = CONSTANTE_GRAV*masse_planete*masse_entite/r2
                    a_grav = Force_grav/masse_entite
                    #on additionne la gravité à celle du moteur(+vecteur unitaire pour la direction)
                    a_planete_x+=a_grav*(delta_x/r)
                    a_planete_y+=a_grav*(delta_y/r)
    return a_planete_x,a_planete_y


def stop_vaisseau():
    get_delta_pos(vaisseau,pygame.time.get_ticks(),0,orientation_vaisseau,True)


def collision_planete():
    global scene

    for entite in scene["planetes"]:
        x_planete , y_planete = entite["position"]
        #distance entre la planete et le vaisseau
        
        delta_x = x_planete-x_vaisseau_ecran
        delta_y = y_planete-y_vaisseau_ecran
        r2 = delta_x**2 + delta_y**2
        rayon_total = entite["rayon"]+RAYON_VAISSEAU
        if r2 <= rayon_total**2:
            pygame.quit()
            sys.exit()
    

def affiche(scene,delta_pos):
    for key in scene.keys():
        for entite in scene[key]:
            entite["position"][0] += delta_pos[0]
            entite["position"][1] += delta_pos[1]
            if key == "planetes":
                afficher_planete(entite)
            elif key == "vaisseau":
                afficher_vaisseau()
            elif key == "etoiles":
                # print(scene["etoiles"])
                pygame.draw.circle(fenetre,WHITE,(entite["position"][0],entite["position"][1]),1)


    coord_txt= police.render("X:" + str(round(position_vaisseau[0])) + ",Y:" + str(round(position_vaisseau[1])), True, WHITE)
    fenetre.blit(coord_txt, (0,0))
    angle_txt= police.render("Angle:" + str(round(orientation_vaisseau,2)) + " deg", True, WHITE)
    fenetre.blit(angle_txt, (0,15))
    vx_txt= police.render("Vitesse X:" + str(round(vaisseau["vitesse_x"],2)), True, WHITE)
    fenetre.blit(vx_txt, (0,30))
    vy_txt= police.render("Vitesse Y:" + str(round(vaisseau["vitesse_y"],2)), True, WHITE)
    fenetre.blit(vy_txt, (0,45))

def afficher_vaisseau():
    image_vaisseau = vaisseau["image"]
    #Il faut rajouter un moins sinon l'image du vaisseau tourne dans le mauvais sens
    photo_vaisseau_r = pygame.transform.rotate(image_vaisseau,-orientation_vaisseau)
    position_vaisseau_photo = pygame.Rect(x_vaisseau_ecran-RAYON_VAISSEAU,y_vaisseau_ecran-RAYON_VAISSEAU,2*RAYON_VAISSEAU,2*RAYON_VAISSEAU)
    fenetre.blit(photo_vaisseau_r,position_vaisseau_photo)


def afficher_planete(planete):
    photo_planete = planete['image']
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
            for planetes_cree in scene["planetes"] : 
                x_planete,y_planete = planetes_cree["position"]
                delta_xp = x_gen_planete-x_planete
                delta_yp = y_gen_planete-y_planete
                dist_planetes2 = delta_xp**2 + delta_yp**2
                distance_min = rayon + planetes_cree["rayon"]+DIST_MIN_ENTRE_PLANETE
                if dist_planetes2 <distance_min**2:
                    peut_placer = False
            if peut_placer:
                
                planete = nouvelle_entite("planete",[x_gen_planete,y_gen_planete],rayon,masse,photo_planete)
                ajouteEntite(scene["planetes"],planete)

def generer_fond_etoile():
    for etoiles in range (NOMBRE_ETOILES):
        print("bonjour")
        x_gen_etoiles = random.randint(-LIMITES_JEU[0],LIMITES_JEU[0])
        y_gen_etoiles = random.randint(-LIMITES_JEU[1],LIMITES_JEU[1])
        etoile = nouvelle_etoile([x_gen_etoiles,y_gen_etoiles])
        ajouteEntite(scene["etoiles"], etoile)
    
        

def nouvelle_etoile(position):
    return{
        "position" : position
    }
               
def nouvelle_entite(type_entite,position_entite,rayon_entite,masse_entite,image=None,orientation_entite=None,vitesse_x_entite=None,vitesse_y_entite=None):
    return{
     'type' : type_entite,
     'position' : position_entite,
     'image' : image,
     'orientation':orientation_entite,
     'rayon' : rayon_entite,
     'masse' : masse_entite,
     'vitesse_x':vitesse_x_entite,
     'vitesse_y':vitesse_y_entite,
     'vitesse_x_avant':0,
     'vitesse_y_avant':0,
     'temps_avant':0,
     'poses' :{}
    }


def ajoute_pose(entite,nom,image):
    entite['poses'][nom] = image

def prends_pose(entite,nom_pose):
    entite['image'] =entite['poses'][nom_pose]

def destroy_entite(scene,entite):
    if entite in scene:
        scene.remove(entite)

def ajouteEntite(scene, entite):
    scene.append(entite)

def allume_moteur(vaisseau_avance):
    
    if vaisseau_avance==False:
        vaisseau_avance = True
        prends_pose(vaisseau,"vaisseau_avance")
    return vaisseau_avance

def eteint_moteur(vaisseau_avance):
    
    vaisseau_avance = False
    prends_pose(vaisseau,"vaisseau_stop")
    return vaisseau_avance
### Boucle de jeu ###

generer_carte()
generer_fond_etoile()
# Création du vaisseau
vaisseau_images =['vaisseau_avance.png','vaisseau_stop.png']

vaisseau = nouvelle_entite('vaisseau',[x_vaisseau_ecran,y_vaisseau_ecran],RAYON_VAISSEAU,masse_vaisseau,None,orientation_vaisseau,0,0)
for image in vaisseau_images:
    loaded_image = pygame.image.load('images/' + image).convert_alpha(fenetre)
    loaded_image = pygame.transform.scale(loaded_image,(RAYON_VAISSEAU*2,RAYON_VAISSEAU*2))
    ajoute_pose(vaisseau,image.replace(".png", ""),loaded_image)

prends_pose(vaisseau,"vaisseau_stop")
ajouteEntite(scene["vaisseau"],vaisseau)
                
print(scene["etoiles"])
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

    fenetre.fill(couleur_fond)

    delta_pos = get_delta_pos(vaisseau,pygame.time.get_ticks(),force_vaisseau,orientation_vaisseau)
   
    affiche(scene, delta_pos)
    
    
    # collision_planete()
    pygame.display.flip()
    horloge.tick(images_par_seconde)
    