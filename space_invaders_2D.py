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

RAYON_PLAYER = 20
RAYON_PLANETE_MIN=100
RAYON_PLANETE_MAX=300
DIST_MIN_ENTRE_PLANETE = 300
VITESSE_MISSILE_INIT = 0.5

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
DISTANCE_AFFICHAGE = 9*dimensions_fenetre[0]**2
temps_avant_recharge = 0
delai_recharge = 200
attente =0
temps_anim_mort =10
pose =0
FACTEUR_GRAVITE_MISSILE = 3



# player
#coordonnés du player dans le repere écran
x_player_ecran,y_player_ecran = dimensions_fenetre[0]/2,dimensions_fenetre[1]/2
position_player = x_player_ecran,y_player_ecran
orientation_player = 0
puissance_player = 1
masse_player = 3000
player_avance = False
vitesse_max_player = 1

#Enemis
vitesse_max_enemis = 0.1

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
    "missiles":[],
    "player":[],
    "enemis":[]
}

police = pygame.font.SysFont('monospace', dimensions_fenetre[1]//50, True)

# Création de listes contenant les images de leur répertoirs respectifs
planetes_images = []
for image_planete in os.listdir("images/planetes/"):
    planetes_images.append(pygame.image.load('images/planetes/' + image_planete).convert_alpha(fenetre))

missile_image = {}
for nom_fichier in ['missile_vie.png','missile_mort_anim_1.png','missile_mort_anim_2.png','missile_mort_anim_3.png']:
    image_missile = pygame.image.load('images/'+nom_fichier).convert_alpha(fenetre)
    image_missile = pygame.transform.scale(image_missile,(RAYON_PLAYER,RAYON_PLAYER))
    nom_pose = nom_fichier.replace('.png', '')
    missile_image[nom_pose] = image_missile


# Fonctions
def mouvement(nom,duree):
    return (nom,duree)

def nomMouvement(mvt):
    return mvt[0]
def dureeMouvement(mvt):
    return mvt[1]
def repete(animation,fois):
    animation['repetition'] = fois
def nouvelleAnimation():
    return{
        'boucle': False,
        'repetition':0,
        'momentMouvementSuivant':None,
        'indexMouvement'   :None,
        'choregraphie':[] 
    }
def ajouteMouvement(animation,mvt):
    animation['choregraphie'].append(mvt)

def commenceMouvement(animation,index):
    animation['indexMouvement'] = index
    animation['momentMouvementSuivant']=pygame.time.get_ticks()+dureeMouvement(animation['choregraphie'][index])

def commence(animation):
    commenceMouvement(animation,0)
def enBoucle(animation):
    animation['boucle'] = True

def arrete(animation):
    animation['indexMouvement']=None
def mouvementActuel(animation):
    if animation['indexMouvement']==None:
        return None
    else:
        return nomMouvement(animation['choregraphie'][animation['indexMouvement']])
    
def anime(animation):
    if animation['indexMouvement']==None:
        commence(animation)
    elif animation['momentMouvementSuivant'] <= pygame.time.get_ticks():
        if animation['indexMouvement'] == len(animation['choregraphie']) - 1:
            if animation['boucle']:
                commence(animation)
            else:
                if animation['repetition'] > 0:
                    animation['repetition'] -= 1
                    commence(animation)
                else:
                    arrete(animation)
        else:
            commenceMouvement(animation, animation['indexMouvement'] + 1)
def commenceAnimation(entite,nomAnimation,fois =1):
    entite['animationActuelle'] = entite['animation'][nomAnimation]
    if fois == 0:
        enBoucle(entite['animationActuelle'])
    else:
        repete(entite['animationActuelle'],fois -1)
def arreteAnimation(entite):
    arrete(entite['animationActuelle'])
    entite['animationActuelle']=None
def ajouteAnimation(entite,nom,animation):
    entite['animation'][nom] = animation

def estEnAnimation(entite):
    return entite['animationActuelle']!=None




def gerer_touche(event):
    global player_avance
    global orientation_player


    if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
        key = event.key
        match key:
            case pygame.K_z:
                #  Le player avance tant que la touche n'est pas lachée
                if event.type == pygame.KEYDOWN:
                    player_avance = allume_moteur(player_avance)    
                elif event.type == pygame.KEYUP:
                    player_avance = eteint_moteur(player_avance)
            case pygame.K_e:
                stop_vaisseau(player)
            case pygame.K_t:
                tir_cannon(temps_maintenant,player)
            case pygame.K_a:
                if event.type == pygame.KEYDOWN:
                    if enemi["avance"]:
                        enemi["avance"] = False
                    else:
                        enemi["avance"] = True
                    #print("Enemi avance = " + str(enemi["avance"]))

# Fonction qui calcule la différence entra l'ancienne et la nouvelle position du player (afin de l'appliquer aux élément du jeu)
def get_delta_pos(entite,temps_maintenant,force_entite,orientation,stop=False):
    
    global position_player
    
    #cordonnés du player dans la map
    x0,y0 = entite["position"]
    if entite["type"] == "player":
        x0,y0 = position_player

    vx0, vy0 = entite["vitesse_x_avant"], entite["vitesse_y_avant"]

    delta_t = temps_maintenant - entite["temps_avant"]
    
    
    angle_rad = math.radians(orientation)
    #récupération de l'accélération du player
    a = force_entite/entite["masse"]
    ax = a*math.cos(angle_rad)
    ay = a*math.sin(angle_rad)
            

    #calcul gravité pour chaque planete
    a_planete_x,a_planete_y = calcul_gravite_planete(entite)
    ax+=a_planete_x
    ay+=a_planete_y

    #mise a jour vitesse
    vx = vx0+ax*delta_t
    vy = vy0+ay*delta_t

    # Vitesse max
    vitesse_max = entite["vitesse_max"]
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


    #mise a jour position du player
    x =x0 + vx0*delta_t + (ax*delta_t**2)/2
    y =y0 + vy0*delta_t + (ay*delta_t**2)/2

    #gestion des colisions du player avec la limite de la map
    if abs(x) > abs(LIMITES_JEU[0]) or abs(y) > abs(LIMITES_JEU[1]) or stop:
        vx = 0
        vy = 0
        entite["vitesse_x_avant"],entite["vitesse_y_avant"] = vx,vy
        entite["temps_avant"] = temps_maintenant
        
        if entite["type"] == "player":
            position_player = [x0,y0]
        return [0,0]
    

    entite["vitesse_x_avant"],entite["vitesse_y_avant"] = vx,vy
    entite["vitesse_x"],entite["vitesse_y"] = vx,vy
    
    entite["temps_avant"] = temps_maintenant
    
    # Nouvelle position du player dans la map
    if entite["type"] == "player":
        position_player = [x,y]
    

    # On retourne la différence entre l'ancienne et nouvelle position du player
    return [x0-x,y0-y]

def calcul_gravite_planete(entite):
    if entite["type"] !="player" and entite["type"] !="missile" and entite["type"] !="enemi":
        return 0,0
    else:
        a_planete_x = 0
        a_planete_y = 0
        masse_entite = entite["masse"]
        x_entite,y_entite = entite["position"]
        for planete in scene['planetes']: 
                    x_planete,y_planete = planete["position"]

                    #distance au carré entre le player et la planete choisie
                    delta_x = x_planete-x_entite
                    delta_y = y_planete-y_entite
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


def stop_vaisseau(vaisseau):
    get_delta_pos(vaisseau,pygame.time.get_ticks(),0,orientation_player,True)



    

def affiche(scene,delta_pos):
    for key in scene.keys():
        for entite in scene[key]:
            
            if key == "player":
                afficher_vaisseau(player)
            else:
                entite["position"][0] += delta_pos[0]
                entite["position"][1] += delta_pos[1]
                rayon = 0
                if "rayon" in entite:
                    rayon = entite["rayon"]

            #Culling
            distance_entite_x = abs(entite["position"][0] - x_player_ecran)-rayon
            distance_entite_y = abs(entite["position"][1] - y_player_ecran) - rayon
            if distance_entite_x <= distance_bord_ecran_x and distance_entite_y <= distance_bord_ecran_y:
                if key == "planetes":
                    afficher_planete(entite)
                elif key == "etoiles":
                    pygame.draw.circle(fenetre,WHITE,(entite["position"][0],entite["position"][1]),1)
                elif key == "enemis":
                    afficher_vaisseau(entite)
                elif key == "missiles":
                    afficher_missile(entite)
                    if entite['animationActuelle']!=None:
                        animationActuelle = entite['animationActuelle']
                        poseActuelle = mouvementActuel(animationActuelle)
                        anime(animationActuelle)
                        nouvellePose = mouvementActuel(animationActuelle)
                        if nouvellePose == None:
                            entite['animationActuelle'] = None
                            destroy_entite(scene['missiles'],entite)
                            if poseActuelle != None:
                                prends_pose(entite,poseActuelle)
                        else:
                            prends_pose(entite,nouvellePose)
                    


                    

                
    coord_txt= police.render("X:" + str(round(position_player[0])) + ",Y:" + str(round(position_player[1])), True, WHITE)
    fenetre.blit(coord_txt, (0,0))
    angle_txt= police.render("Angle:" + str(round(orientation_player,2)) + " deg", True, WHITE)
    fenetre.blit(angle_txt, (0,15))
    vx_txt= police.render("Vitesse X:" + str(round(player["vitesse_x"],2)), True, WHITE)
    fenetre.blit(vx_txt, (0,30))
    vy_txt= police.render("Vitesse Y:" + str(round(player["vitesse_y"],2)), True, WHITE)
    fenetre.blit(vy_txt, (0,45))

def afficher_vaisseau(vaisseau):
    image_vaisseau = vaisseau["image"]
    x,y = vaisseau["position"]
    if vaisseau["type"] == "player":
        x,y = x_player_ecran,y_player_ecran

    #Il faut rajouter un moins sinon l'image du vaisseau tourne dans le mauvais sens
    photo_vaisseau_r = pygame.transform.rotate(vaisseau["image"],-vaisseau["orientation"])
    position_vaisseau_photo = pygame.Rect(x-vaisseau["rayon"],y-vaisseau["rayon"],2*vaisseau["rayon"],2*vaisseau["rayon"])
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
        delta_x = x_gen_planete - position_player[0]
        delta_y = y_gen_planete -position_player[1]
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
        x_gen_etoiles = random.randint(-LIMITES_JEU[0],LIMITES_JEU[0])
        y_gen_etoiles = random.randint(-LIMITES_JEU[1],LIMITES_JEU[1])
        etoile = nouvelle_etoile([x_gen_etoiles,y_gen_etoiles])
        ajouteEntite(scene["etoiles"], etoile)
    
        

def nouvelle_etoile(position):
    return{
        "position" : position
    }
               
def nouvelle_entite(type_entite,position_entite,rayon_entite,masse_entite,image=None,orientation_entite=None,vitesse_x_entite=None,vitesse_y_entite=None,vitesse_max=1,delai_vie=None):
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
     'poses' :{},
     'vitesse_max' : vitesse_max,
     'avance': False,
     'duree_vie':delai_vie,
     'animationActuelle':None,
     'animation':{}
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

def allume_moteur(player_avance):
    
    if player_avance==False:
        player_avance = True
        prends_pose(player,"player_avance")
    return player_avance

def eteint_moteur(player_avance):
    
    player_avance = False
    prends_pose(player,"player_stop")
    return player_avance

# Création du vaisseau
player_images =['player_avance.png','player_stop.png']

player = nouvelle_entite('player',[x_player_ecran,y_player_ecran],RAYON_PLAYER,masse_player,None,orientation_player,0,0) #player["position"] est la position fixe à l'écran
for image in player_images:
    loaded_image = pygame.image.load('images/' + image).convert_alpha(fenetre)
    loaded_image = pygame.transform.scale(loaded_image,(RAYON_PLAYER*2,RAYON_PLAYER*2))
    ajoute_pose(player,image.replace(".png", ""),loaded_image)

prends_pose(player,"player_avance")
ajouteEntite(scene["player"],player)

distance_bord_ecran_x = abs(x_player_ecran+RAYON_PLAYER)
distance_bord_ecran_y = abs(y_player_ecran+RAYON_PLAYER)


def tir_cannon(temps_maintenant,entite):
    global temps_avant_recharge
    delai = temps_maintenant-temps_avant_recharge
    if delai > delai_recharge:
        orientation_missile = entite["orientation"]
        missile = nouvelle_entite('missile',[x_player_ecran,y_player_ecran],RAYON_PLAYER,0.5*masse_player,None,orientation_missile,0,0,900,200)
        angle_rad_missile = math.radians(orientation_missile)
        vitesse_x_vaisseau = entite['vitesse_x']
        vitesse_y_vaisseau = entite['vitesse_y']
        missile['vitesse_x'] =vitesse_x_vaisseau + VITESSE_MISSILE_INIT*math.cos(angle_rad_missile)
        missile['vitesse_y'] =vitesse_y_vaisseau + VITESSE_MISSILE_INIT*math.sin(angle_rad_missile)
        missile['poses']= missile_image
        prends_pose(missile,'missile_vie')
        ajouteEntite(scene["missiles"],missile)
        ajouteAnimation(missile,'animation_mort_missile',animation_missile())
        temps_avant_recharge = temps_maintenant
        
    return


def animation_missile():
    animation_mort_missile = nouvelleAnimation()
    ajouteMouvement(animation_mort_missile,mouvement('missile_mort_anim_1',200))
    ajouteMouvement(animation_mort_missile,mouvement('missile_mort_anim_2',200))
    ajouteMouvement(animation_mort_missile,mouvement('missile_mort_anim_3',500))
    return animation_mort_missile


def autodestruction_missile(missile):
    delai_vie  = missile["duree_vie"]
    if delai_vie<=0 and estEnAnimation(missile)==0:
            commenceAnimation(missile,'animation_mort_missile',1)
    return


def afficher_missile(missile):
    image_missile = missile["image"]
    if missile["type"] == "missile":
        x,y = missile["position"]

    #Il faut rajouter un moins sinon l'image du vaisseau tourne dans le mauvais sens
    image_missile = pygame.transform.rotate(missile["image"],-missile["orientation"])
    fenetre.blit(image_missile,(x,y))
    return

def mise_a_jour_etat_missile(delta_t):
    for missile in scene['missiles']:
        a_planete_x , a_planete_y = calcul_gravite_planete(missile)
        missile["vitesse_x"]+=a_planete_x*delta_t*FACTEUR_GRAVITE_MISSILE
        missile["vitesse_y"]+=a_planete_y*delta_t*FACTEUR_GRAVITE_MISSILE

        missile["position"][0]+=missile["vitesse_x"]*delta_t
        missile["position"][1]+=missile["vitesse_y"]*delta_t
        missile["duree_vie"]-=1
        autodestruction_missile(missile)


enemi = nouvelle_entite("enemi",[500,500],RAYON_PLAYER,3000,None,0,None,None,0.5)
image_enemi = pygame.image.load("images/enemis/ship.png").convert_alpha(fenetre)
image_enemi = pygame.transform.scale(image_enemi,(enemi["rayon"]*2,enemi["rayon"]*2))
ajoute_pose(enemi,"ship",image_enemi)
prends_pose(enemi,"ship")
ajouteEntite(scene["enemis"],enemi)

def ai_enemi(enemi):
    xp,yp = x_player_ecran,y_player_ecran
    delta_x_player = xp-enemi["position"][0]
    delta_y_player = yp-enemi["position"][1]
    distance2_player = delta_x_player**2 + delta_y_player**2
    force_enemi = 0
    enemi["vitesse_max"] = 0

    if distance2_player >= 300**2:
        enemi["avance"] = True
    else:
        enemi["avance"] = False
    
    orientation_enemi = math.degrees(math.atan2(delta_y_player,delta_x_player))%360

    #Planete la plus proche de l'enemi
    index_planete =  collision_planetes(enemi)
    planete = scene["planetes"][index_planete]

    x_planete, y_planete = planete["position"]

    delta_x_planete = x_planete-enemi["position"][0]
    delta_y_planete = y_planete-enemi["position"][0]

    #Distance au carré entre la planete la plus proche et l'enemi (EST NEGATIVE SI DANS LA PLANETE)
    distance2_planete = delta_x_planete**2 + delta_y_planete**2 -(planete["rayon"]+RAYON_PLAYER)**2
    if distance2_planete<=200**2:
        enemi["avance"] = True
        orientation_enemi = ((math.degrees(math.atan2(delta_y_planete,delta_x_planete)))%360)-180
        # orientation_enemi = (orientation_enemi-180)%360
        force_enemi= 10
        enemi["vitesse_max"] = 1
        # print("force_enemi = " + str(force_enemi))
        # print("enemi vitesse X = " + str(enemi["vitesse_x"]))
        # print("enemi vitesse Y = " + str(enemi["vitesse_y"]))

    enemi["orientation"] = orientation_enemi
    delta_pos=[0,0]
    if enemi["avance"]:
        force_enemi = 0.1
    else:
        force_enemi = 0
    delta_pos = get_delta_pos(enemi,pygame.time.get_ticks(),force_enemi,orientation_enemi)
    # print("Enemi avance = " + str(enemi["avance"]))
    enemi["position"][0] -= delta_pos[0]
    enemi["position"][1] -= delta_pos[1]
    #print(enemi["position"])


def collision_planetes(entite):
    xp,yp = entite["position"]
    list_distances2_planetes = []
    index_planete = 0
    index_planete_proche = 0
    min_dist = float(math.inf)
    for index, planete in enumerate(scene["planetes"]):
        x_planete , y_planete = planete["position"]
        #distance entre la planete et l'entite
        delta_x = x_planete-xp
        delta_y = y_planete-yp
        r2 = delta_x**2 + delta_y**2
        rayon_total = planete["rayon"]+RAYON_PLAYER
        if entite["type"] == "enemi":
            #la distance au carré entre le bord de la planete et le bord de l'entite
            distance2_planete = r2-(rayon_total**2)
            if distance2_planete < min_dist:
                min_dist = distance2_planete
                index_planete_proche = index
        index_planete+=1
        if entite["type"] == "player" and r2 <= rayon_total**2:
            pygame.quit()
            sys.exit()
        #print("index = " + str(index_planete))
    #retourne l'index dans scene["planetes"] de la planete la plus proche de l'entite
    #print("len = "+ str(len(scene["planetes"])))
    #print("index final = " + str(index_planete_proche))
    return index_planete_proche


generer_carte()
generer_fond_etoile()
dernier_temps_missiles = pygame.time.get_ticks()
### Boucle de jeu ###
while True:
    temps_maintenant = pygame.time.get_ticks()
    delta_t_missile = temps_maintenant-dernier_temps_missiles
    dernier_temps_missiles = pygame.time.get_ticks()

    for event in pygame.event.get():
        gerer_touche(event)


    mouse_x,mouse_y = pygame.mouse.get_pos()
    delta_mouse_x, delta_mouse_y = mouse_x-x_player_ecran, mouse_y-y_player_ecran

    # Calcul du nouvel angle du vaisseau par rapport à la position de la souris (modulo 360)
    angle_rad = math.atan2(delta_mouse_y,delta_mouse_x)
    orientation_player = (math.degrees(angle_rad))%360
    player["orientation"] = orientation_player

    if player_avance:
        force_player = puissance_player
    else:
        force_player = 0

    fenetre.fill(couleur_fond)

    for enemi in scene["enemis"]:
        ai_enemi(enemi)
    
    mise_a_jour_etat_missile(delta_t_missile)
    

    delta_pos = get_delta_pos(player,pygame.time.get_ticks(),force_player,orientation_player)
    

    affiche(scene, delta_pos)
    
    # collision_planetes(player)
    pygame.display.flip()
    horloge.tick(images_par_seconde)
    