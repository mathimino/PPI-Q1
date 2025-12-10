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
VITESSE_MISSILE_INIT = 0.5

LIMITES_JEU = [10000,10000]

RAYON_INFLUENCE = 1000
CONSTANTE_GRAV = 0.0001

#genereation carte
NBR_PLANETE_MIN = 750
NBR_PLANETE_MAX=1000
NOMBRE_ETOILES = 10000
global nombre_vies
nombre_vies = 3
NOMBRE_VIES_INIT=3
highscore = 1000000


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
global enjeu
enjeu = False


# player
#coordonnés du player dans le repere écran
x_player_ecran,y_player_ecran = dimensions_fenetre[0]/2,dimensions_fenetre[1]/2
position_player = x_player_ecran,y_player_ecran
orientation_player = 0
puissance_player = 1
masse_player = 3000
player_avance = False
vitesse_max_player = 1

#Ennemis
CPT_REVERSE = 50
CPT_SHOT = 25
VITESSE_MAX_ENNEMIS = 0.2
DISTANCE_REVERSE_PLANETE = 75
DISTANCE2_AVANCE_ENNEMIS = 160000 #400**2
FORCE_ENNEMIS = 0.3
global dernier_spawn_ennemi
dernier_spawn_ennemi = 0
NBR_ENNEMIS_MAX = 10
TEMPS_SPAWN_ENNEMIS_MIN = 3
ennemis_images = ["ship_avance.png","ship_stop.png"]
DUREE_VIE_ENNEMIS = 60


# Initialisation

pygame.init()
pygame.mixer.init()

fenetre = pygame.display.set_mode(dimensions_fenetre)
pygame.display.set_caption("Space Invaders 2D")
pygame.key.set_repeat(10, 10)

horloge = pygame.time.Clock()
couleur_fond = NOIR

scene = {
    "etoiles":[],
    "planetes" : [],
    "entites" : [],
    "missiles":[],
    "player":[],
    "ennemis":[]
}

police = pygame.font.SysFont('monospace', dimensions_fenetre[1]//50, True)

# Création de listes contenant les images de leur répertoirs respectifs
planetes_images = []
for image_planete in os.listdir("images/planetes/"):
    planetes_images.append(pygame.image.load('images/planetes/' + image_planete).convert_alpha(fenetre))

missile_nom_pose = ['missile_vie','missile_mort_anim_1','missile_mort_anim_2','missile_mort_anim_3']
missile_images = []
for nom_fichier in ['missile_vie.png','missile_mort_anim_1.png','missile_mort_anim_2.png','missile_mort_anim_3.png']:
    image_missile = pygame.image.load('images/'+nom_fichier).convert_alpha(fenetre)
    image_missile = pygame.transform.scale(image_missile,(RAYON_VAISSEAU,RAYON_VAISSEAU))
    missile_images.append(image_missile)


    



images_menu = pygame.image.load('images/menu_fond.png').convert_alpha(fenetre)
image_titre = pygame.image.load('images/menu_titre.png').convert_alpha(fenetre)
image_titre= pygame.transform.scale(image_titre,(dimensions_fenetre[0],dimensions_fenetre[1]/2))
image_coeur = pygame.image.load('images/vie_joueur.png').convert_alpha(fenetre)
image_coeur= pygame.transform.scale(image_coeur,(dimensions_fenetre[0]/10,dimensions_fenetre[0]/10))


# Fonctions animation
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
    
def ajoute_pose(entite,nom,image):
    entite['poses'][nom] = image

def prends_pose(entite,nom_pose):
    entite['image'] = entite['poses'][nom_pose]  
    entite["rect"] = entite["image"].get_rect(center=(entite["position"]))
    
def estEnAnimation(entite):
    return entite['animationActuelle']!=None

def animation_missile():

    animation_mort = nouvelleAnimation()
    ajouteMouvement(animation_mort,mouvement('missile_mort_anim_1',200))
    ajouteMouvement(animation_mort,mouvement('missile_mort_anim_2',200))
    ajouteMouvement(animation_mort,mouvement('missile_mort_anim_3',500))
    return animation_mort

def animation_mort_globale(entite,scene):
    global enjeu,nombre_vies
    if entite['animationActuelle']!=None:
                        # print("animation mtn = " + str(entite['animationActuelle']))
                        animationActuelle = entite['animationActuelle']
                        poseActuelle = mouvementActuel(animationActuelle)
                        # print(ennemi)
                        anime(animationActuelle)
                        nouvellePose = mouvementActuel(animationActuelle)
                        if nouvellePose == None:
                            entite['animationActuelle'] = None
                            if entite["type"]== "player":
                                enjeu = False
                                nombre_vies -=1
                            destroy_entite(scene,entite)
                                
                            if poseActuelle != None:
                                prends_pose(entite,poseActuelle)
                        else:
                            prends_pose(entite,nouvellePose)
#fonction generale entite
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
     'animation':{},
     'cpt_reverse': -1,
     'cpt_shot': 0,
     'rect': None
    }
def destroy_entite(scene,entite):
    if entite in scene:
        scene.remove(entite)

def ajouteEntite(scene, entite):
    scene.append(entite)
    
def explosion_taille(entite,facteur_explosion):
    explosion_taille =entite["rayon"]*2*facteur_explosion
    explosion_enti_1 = pygame.transform.scale(missile_images[1],(explosion_taille,explosion_taille))
    explosion_enti_2 = pygame.transform.scale(missile_images[2],(explosion_taille,explosion_taille))
    explosion_enti_3 = pygame.transform.scale(missile_images[3],(explosion_taille,explosion_taille))
    ajoute_pose(entite, "missile_mort_anim_1", explosion_enti_1)
    ajoute_pose(entite, "missile_mort_anim_2", explosion_enti_2)
    ajoute_pose(entite, "missile_mort_anim_3", explosion_enti_3)
#fonction vaisseau
def cree_vaisseau():
    global player
    player_images =['player_avance.png','player_stop.png']

    player = nouvelle_entite('player',[x_player_ecran,y_player_ecran],RAYON_VAISSEAU,masse_player,None,orientation_player,0,0) #player["position"] est la position fixe à l'écran
    for image in player_images:
        loaded_image = pygame.image.load('images/' + image).convert_alpha(fenetre)
        loaded_image = pygame.transform.scale(loaded_image,(RAYON_VAISSEAU*2,RAYON_VAISSEAU))
        ajoute_pose(player,image.replace(".png", ""),loaded_image)
    explosion_taille(player,2)
    prends_pose(player,"player_stop")
    ajouteEntite(scene["player"],player)
    ajouteAnimation(player,"animation_mort",animation_missile())
    return 

def allume_moteur(player_avance):
    
    if player_avance==False:
        player_avance = True
        prends_pose(player,"player_avance")
    return player_avance

def eteint_moteur(player_avance):
    player_avance = False
    prends_pose(player,"player_stop")
    return player_avance

def stop_vaisseau(vaisseau):
    get_delta_pos(vaisseau,pygame.time.get_ticks(),0,orientation_player,True)

#fonction de deplacement
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
    # a_planete_x,a_planete_y = calcul_gravite_planete(entite)
    # ax+=a_planete_x
    # ay+=a_planete_y

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
    if entite["type"] !="player":# and entite["type"] !="missile": #and entite["type"] !="ennemi":
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


#fonction de generation
def nouvelle_etoile(position):
    return{
        "position" : position
    }
               
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


#fonctions d'affichage
def afficher_planete(planete):
    photo_planete = planete['image']
    position = pygame.Rect(planete['position'][0]-planete['rayon'],planete['position'][1]-planete['rayon'],2*planete['rayon'],2*planete['rayon'])
    fenetre.blit(photo_planete,position)
    return


def afficher_vaisseau(vaisseau):
    x,y = vaisseau["position"]
    if vaisseau["type"] == "player":
        x,y = x_player_ecran,y_player_ecran

    if vaisseau["type"] == "ennemi" and not estEnAnimation(vaisseau):
        if vaisseau["avance"]:
            prends_pose(vaisseau,"ship_avance")
        else:
            prends_pose(vaisseau,"ship_stop")
    
      #Il faut rajouter un moins sinon l'image du vaisseau tourne dans le mauvais sens
    photo_vaisseau_r = pygame.transform.rotate(vaisseau["image"],-vaisseau["orientation"])
    
    vaisseau["rect"]= photo_vaisseau_r.get_rect(center = (x,y))
    
    fenetre.blit(photo_vaisseau_r,vaisseau["rect"])
    pygame.draw.rect(fenetre, ROUGE, vaisseau["rect"], 1)


def afficher_missile(missile):
    image_missile = missile["image"]
    if missile["type"] == "missile":
        x,y = missile["position"]

    #Il faut rajouter un moins sinon l'image du vaisseau tourne dans le mauvais sens
    image_missile = pygame.transform.rotate(missile["image"],-missile["orientation"])
    missile["rect"] = image_missile.get_rect(center = (x,y))
    fenetre.blit(image_missile,missile["rect"])
    pygame.draw.rect(fenetre, ROUGE, missile["rect"], 1)
    # if player["rect"].collidepoint(x,y):
    #     print("touche")
    
    return   


def afficher_menu():
    global nombre_vies
    fenetre.fill(couleur_fond)
    fenetre.blit(images_menu,(0,0))
    fenetre.blit(image_titre,(10,50))
    temps_titre = pygame.time.get_ticks()
    texte_meilleur_score = police.render(("HIGHSCORE :"),True,WHITE)
    texte_score = police.render(str(round(highscore)),True,WHITE)
    texte_meilleur_score = pygame.transform.scale(texte_meilleur_score,(dimensions_fenetre[0]/4,dimensions_fenetre[1]/28))
    if (temps_titre//1000)%3!=0:

        commenceJouer= police.render(("Appuyez pour commencer"), True, JAUNE)
        commenceJouer = pygame.transform.scale(commenceJouer,(dimensions_fenetre[0]/2,dimensions_fenetre[1]/14))
        fenetre.blit(commenceJouer,(dimensions_fenetre[0]/4,300))

        text_controls = police.render(("Controler le vaisseau avec Z et le curseur de souris"), True, WHITE)
        text_controls = pygame.transform.scale(text_controls,(9*dimensions_fenetre[0]/10,dimensions_fenetre[1]/17))
        fenetre.blit(text_controls,(dimensions_fenetre[0]/20,400))
        
        text_shoot = police.render(("Tirez avec un click de la souris"), True, WHITE)
        text_shoot = pygame.transform.scale(text_shoot,(4*dimensions_fenetre[0]/5,dimensions_fenetre[1]/17))
        fenetre.blit(text_shoot,(dimensions_fenetre[0]/10,500))

        if nombre_vies<NOMBRE_VIES_INIT:
            fenetre.blit(texte_meilleur_score,(3*dimensions_fenetre[0]/8,20))
            fenetre.blit(texte_score,(5*dimensions_fenetre[0]/8,27))
        
    for i in range(nombre_vies):
        fenetre.blit(image_coeur,(dimensions_fenetre[0]/2-(nombre_vies/2)*dimensions_fenetre[0]/10+i*dimensions_fenetre[0]/10,dimensions_fenetre[1]-200))


def affiche(scene,delta_pos):
    for key in scene.keys():
        for entite in scene[key]:
            
            
            if key == "player":
                afficher_vaisseau(player)
                animation_mort_globale(entite,scene["player"])
            else:
                entite["position"][0] += delta_pos[0]
                entite["position"][1] += delta_pos[1]
                rayon = 0
                if "rayon" in entite:
                    rayon = entite["rayon"]
                if key =="missiles":
                    animation_mort_globale(entite,scene["missiles"])
                if key =="ennemis":
                    animation_mort_globale(entite,scene["ennemis"])
                
            #Culling
            distance_entite_x = abs(entite["position"][0] - x_player_ecran)-rayon
            distance_entite_y = abs(entite["position"][1] - y_player_ecran) - rayon
            if distance_entite_x <= distance_bord_ecran_x and distance_entite_y <= distance_bord_ecran_y:
                if key == "planetes":
                    afficher_planete(entite)
                elif key == "etoiles":
                    pygame.draw.circle(fenetre,WHITE,(entite["position"][0],entite["position"][1]),1)
                elif key == "ennemis":
                    afficher_vaisseau(entite)
                elif key == "missiles":
                    afficher_missile(entite)
           

                    
                    


                    

                
    coord_txt= police.render("X:" + str(round(position_player[0])) + ",Y:" + str(round(position_player[1])), True, WHITE)
    fenetre.blit(coord_txt, (0,0))
    angle_txt= police.render("Angle:" + str(round(orientation_player,2)) + " deg", True, WHITE)
    fenetre.blit(angle_txt, (0,15))
    vx_txt= police.render("Vitesse X:" + str(round(player["vitesse_x"],2)), True, WHITE)
    fenetre.blit(vx_txt, (0,30))
    vy_txt= police.render("Vitesse Y:" + str(round(player["vitesse_y"],2)), True, WHITE)
    fenetre.blit(vy_txt, (0,45))


#fonctions missiles
def tir_cannon(temps_maintenant,entite):
    global temps_avant_recharge
    delai = temps_maintenant-temps_avant_recharge
    if delai > delai_recharge:
        orientation_missile = entite["orientation"]
        x,y= entite["position"]
        if entite["type"] == "player":
            x,y = x_player_ecran,y_player_ecran 
            
        missile = nouvelle_entite('missile',[x,y],RAYON_VAISSEAU/2,1000,None,orientation_missile,0,0,900,200)
        angle_rad_missile = math.radians(orientation_missile)
        missile['vitesse_x'] = entite["vitesse_x"] + VITESSE_MISSILE_INIT*math.cos(angle_rad_missile)
        missile['vitesse_y'] = entite["vitesse_y"] + VITESSE_MISSILE_INIT*math.sin(angle_rad_missile)
        for index,item in enumerate(missile_nom_pose):
            ajoute_pose(missile,item,missile_images[index])
        missile["Temps_spawn"]= temps_maintenant
        prends_pose(missile,'missile_vie')
        ajouteEntite(scene["missiles"],missile)
        ajouteAnimation(missile,'animation_mort',animation_missile())
        temps_avant_recharge = temps_maintenant
    return
def autodestruction_missile(missile):
    delai_vie  = missile["duree_vie"]
    if (delai_vie<=0 and estEnAnimation(missile)==0) :
            commenceAnimation(missile,'animation_mort',1)
    return
def mise_a_jour_etat_missile(delta_t):
    for missile in scene['missiles']:
        if not estEnAnimation(missile):
            a_planete_x , a_planete_y = calcul_gravite_planete(missile)
            missile["vitesse_x"]+=a_planete_x*delta_t*FACTEUR_GRAVITE_MISSILE
            missile["vitesse_y"]+=a_planete_y*delta_t*FACTEUR_GRAVITE_MISSILE

            missile["position"][0]+=missile["vitesse_x"]*delta_t
            missile["position"][1]+=missile["vitesse_y"]*delta_t
            missile["duree_vie"]-=1
            autodestruction_missile(missile)

#fonctions collisions
def collision_planetes(entite):
    global scene

    xp,yp = entite["position"]
    index_planete_proche = 0
    min_dist = float(math.inf)
    #on parcours toutes les planetes
    for index, planete in enumerate(scene["planetes"]):
        x_planete , y_planete = planete["position"]
        delta_x = x_planete-xp
        delta_y = y_planete-yp
        #distance au carré entre la planete et l'entite
        r2 = delta_x**2 + delta_y**2
        rayon_total = planete["rayon"]+RAYON_VAISSEAU

        if entite["type"] == "ennemi":
            # On cherche la planete la plus proche de l'ennemi
            #la distance entre le bord de la planete et le bord de l'entite
            distance_planete = abs(math.sqrt(r2)-rayon_total)
            if distance_planete < min_dist and distance_planete>0:
                min_dist = distance_planete
                index_planete_proche = index
            
            if r2 <= rayon_total**2 and not estEnAnimation(ennemi):
                commenceAnimation(entite,"animation_mort",1)

        if entite["type"] == "player" and r2 <= rayon_total**2:
            commenceAnimation(entite,"animation_mort",1)
            # print()

    # on retourne l'index de la planete la plus proche de l'ennemi
    return index_planete_proche
    
def test_collsion(entite1,entite2):
    entite1_x ,entite1_y= entite1["position"]
    entite2_x ,entite2_y= entite2["position"]
    rayon_entite_1 = entite1["rayon"]
    rayon_entite_2 = entite2["rayon"]
    delta_entite_x = entite1_x-entite2_x
    delta_entite_y = entite1_y-entite2_y
    distance_entite_carre = delta_entite_x**2+delta_entite_y**2
    if distance_entite_carre<=(rayon_entite_1+rayon_entite_2)**2:
        return True
    else:
        return False  

# def gerer_collision_generale():
#     global nombre_vies
#     for missile in scene["missiles"]:
#         for planete in scene["planetes"]:
#             if test_collsion(missile,planete):
#                 missile["vitesse_x"]=0
#                 missile["vitesse_y"]=0
#                 if not estEnAnimation(missile):
#                     commenceAnimation(missile,'animation_mort',1)
#         for ennemi in scene["ennemis"]:
#             if test_collsion(missile,ennemi):
#                 if not estEnAnimation(missile):
#                     commenceAnimation(missile,'animation_mort',1)
#                 if not estEnAnimation(ennemi):
#                     commenceAnimation(ennemi,'animation_mort',1)
#         for missile2 in scene["missiles"]:
#             if missile is not missile2:
#                 if test_collsion(missile,missile2):
#                     if not estEnAnimation(missile):
#                         commenceAnimation(missile,'animation_mort',1)
#                     if not estEnAnimation(missile2):
#                         commenceAnimation(missile2,'animation_mort',1)
#         if temps_maintenant-missile["Temps_spawn"]>200:
#             if test_collsion(player,missile):
                
#                 if not estEnAnimation(missile):
#                     commenceAnimation(missile,"animation_mort",1)
#                 if not estEnAnimation(player):
#                     commenceAnimation(player,"animation_mort",1)
#     for planete in scene["planetes"]:
#         if test_collsion(player,planete):
            
#             if not estEnAnimation(player):
#                 commenceAnimation(player,"animation_mort",1)
#         for ennemi in scene["ennemis"]:
#             if test_collsion(ennemi,planete):
#                 if not estEnAnimation(ennemi):
#                     commenceAnimation(ennemi,'animation_mort',1)
                




    return
#fonctions (autres)
def gerer_touche(event):
    global player_avance
    global orientation_player
    global enjeu
    if event.type == pygame.QUIT:
            musique.stop()  
            pygame.display.quit()
            pygame.quit()
            exit()
    if event.type == pygame.MOUSEBUTTONDOWN:
        tir_cannon(pygame.time.get_ticks(),player)
    if enjeu:
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            if not estEnAnimation(player):
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
                   
    elif not enjeu and (event.type == pygame.KEYDOWN or event.type == pygame.KEYUP):
        enjeu = True
        temps_reset =pygame.time.get_ticks()
        for key in scene:
            for entite in scene[key]:
                entite["temps_avant"]=temps_reset
        dernier_temps_missiles = temps_reset    
        


def ai_ennemi(ennemi):
    #Distance au carré entre l'ennemi et le player
    delta_x_player = x_player_ecran-ennemi["position"][0]
    delta_y_player = y_player_ecran-ennemi["position"][1]
    distance2_player = delta_x_player**2 + delta_y_player**2

    #on avance l'ennemi si il est trop loin du player
    if distance2_player >= DISTANCE2_AVANCE_ENNEMIS:
        ennemi["avance"] = True
    else:
        ennemi["avance"] = False
    #l'orientation de l'ennemi est dirigée vers le player
    orientation_ennemi = math.degrees(math.atan2(delta_y_player,delta_x_player))%360

    #On récupère l'indexe de la planete la plus proche de l'ennemi
    index_planete =  collision_planetes(ennemi)
    planete = scene["planetes"][index_planete]
    x_planete, y_planete = planete["position"]

    # Distance au carré entre la planete la plus proche et l'ennemi
    delta_x_planete = x_planete-ennemi["position"][0]
    delta_y_planete = y_planete-ennemi["position"][1]
    #distance entre le centre de la planete et l'ennemi
    distance2_centre_planete = delta_x_planete**2 + delta_y_planete**2
    #calcul de la distance entre le bord de la planete et le bord de l'ennemi
    rayon_total = planete["rayon"]+RAYON_VAISSEAU
    distance_planete = abs(math.sqrt(distance2_centre_planete)-rayon_total)

    # dessin des aides visuelles pour l'ia
    pygame.draw.circle(fenetre, ROUGE, planete["position"],rayon_total+DISTANCE_REVERSE_PLANETE, 3)
    
    pygame.draw.line(fenetre,(0,255,0),ennemi["position"],planete["position"], 3)
    if distance2_player >= DISTANCE2_AVANCE_ENNEMIS:
        pygame.draw.line(fenetre,(138,43,226),ennemi["position"],[x_player_ecran,y_player_ecran], 3)
    else:
        pygame.draw.line(fenetre,ORANGE,ennemi["position"],[x_player_ecran,y_player_ecran], 3)


    force_ennemi = 0
    if ennemi["avance"]:
        force_ennemi = FORCE_ENNEMIS

    #Si l'ennemi est trop proche d'une planete
    if distance_planete<=DISTANCE_REVERSE_PLANETE:
        # on calcule son orientation par rapport au centre de la planete
        orientation_ennemi = ((math.degrees(math.atan2(delta_y_planete,delta_x_planete)))%360)-180
        # on démare un timer
        if ennemi["cpt_reverse"] == -1:
           ennemi["cpt_reverse"] = CPT_REVERSE

    #tant que le timer n'est pas fini, on applique une force plus grande que la normale
    if ennemi["cpt_reverse"] <= CPT_REVERSE and ennemi["cpt_reverse"] > -1:
        force_ennemi= 0.5
        ennemi["cpt_reverse"] -= 1
        ennemi["avance"] = True

    
    #timer pour savoir si on peux tirer de nouveau
    if ennemi["cpt_shot"] >= 0:
        ennemi["cpt_shot"]-=1

    if ennemi["cpt_shot"] == -1:
        ennemi["cpt_shot"]= CPT_SHOT
        # Quanf le timer est fini, on a 50% de chance de tirer
        can_shoot = random.randint(1,2)
        # print(can_shoot)
        if can_shoot == 1 :
            # print("shot!")
            tir_cannon(pygame.time.get_ticks(),ennemi)


    ennemi["orientation"] = orientation_ennemi
    delta_pos = get_delta_pos(ennemi,pygame.time.get_ticks(),force_ennemi,orientation_ennemi)
    ennemi["position"][0] -= delta_pos[0]
    ennemi["position"][1] -= delta_pos[1]

def spawn_enemis():
    global dernier_spawn_ennemi


    nbr_ennemis = len(scene["ennemis"])+1

    spawn_random = random.randint(1,40)
    spawn_time = pygame.time.get_ticks()//1000 #en secondes piles

    # print(dernier_spawn_ennemi!=spawn_time)

    if nbr_ennemis<=NBR_ENNEMIS_MAX and dernier_spawn_ennemi!=spawn_time and spawn_random==1 and (spawn_time%TEMPS_SPAWN_ENNEMIS_MIN)==0:
        dernier_spawn_ennemi = spawn_time
        print("spawn")
        
        x=0
        y=0
        match random.randint(1,4):
            case 1:
                #Côté haut
                x = random.randint(0,dimensions_fenetre[0])
                y = -(RAYON_VAISSEAU*3)
            case 2:
                #Côté droit
                x = dimensions_fenetre[0] + RAYON_VAISSEAU*3
                y = random.randint(0,dimensions_fenetre[1])
            case 3:
                #Côté bas
                x = random.randint(0,dimensions_fenetre[0])
                y = dimensions_fenetre[1] + RAYON_VAISSEAU*3
            case 4:
                #Côté gauche
                x = -(RAYON_VAISSEAU*3)
                y = random.randint(0,dimensions_fenetre[1])


        ennemi = nouvelle_entite("ennemi",[x,y],RAYON_VAISSEAU,3000,None,0.3,0,0,VITESSE_MAX_ENNEMIS,DUREE_VIE_ENNEMIS)
        
        for image in ennemis_images:
            loaded_image = pygame.image.load('images/ennemis/' + image).convert_alpha(fenetre)
            loaded_image = pygame.transform.scale(loaded_image,(ennemi["rayon"]*2,ennemi["rayon"]*2))
            ajoute_pose(ennemi,image.replace(".png", ""),loaded_image)
        for index,item in enumerate(missile_nom_pose):
                ajoute_pose(ennemi,item,missile_images[index])
        prends_pose(ennemi,"ship_stop")
        ajouteAnimation(ennemi,'animation_mort',animation_missile())
        explosion_taille(ennemi,2)
        ajouteEntite(scene["ennemis"],ennemi)




def despawn_ennemis():
    for ennemi in scene["ennemis"]:
        # si l'ennemi est hors de l'écran
        if abs(ennemi["position"][0]) < 0 or abs(ennemi["position"][0]) > dimensions_fenetre[0] \
            or abs(ennemi["position"][1]) < 0 or abs(ennemi["position"][1]) > dimensions_fenetre[1]:
            ennemi["duree_vie"] -= 1
            if ennemi["duree_vie"] < 0:
                destroy_entite(scene["ennemis"],ennemi)
        else:
            ennemi["duree_vie"] = DUREE_VIE_ENNEMIS






# Création du vaisseau
distance_bord_ecran_x = abs(x_player_ecran+RAYON_VAISSEAU)
distance_bord_ecran_y = abs(y_player_ecran+RAYON_VAISSEAU)


cree_vaisseau()
generer_carte()
generer_fond_etoile()
dernier_temps_missiles = pygame.time.get_ticks()


musique = pygame.mixer.Sound("sons/musique_fond.wav")
# musique.play(loops=-1)

### Boucle de jeu ###
while True:
    for event in pygame.event.get():
            gerer_touche(event)
    if enjeu:
        temps_maintenant = pygame.time.get_ticks()
        delta_t_missile = temps_maintenant-dernier_temps_missiles
        dernier_temps_missiles = pygame.time.get_ticks()
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

        spawn_enemis()
        despawn_ennemis()

        for ennemi in scene["ennemis"]:
            if not estEnAnimation(ennemi):
                ai_ennemi(ennemi)

                
        mise_a_jour_etat_missile(delta_t_missile)
        

        delta_pos = get_delta_pos(player,pygame.time.get_ticks(),force_player,orientation_player)
        
        affiche(scene, delta_pos)
       # gerer_collision_generale()
        # collision_planetes(player)
        # print(player["rect"].colliderect(ennemi["rect"]))
    if not enjeu:
        afficher_menu()
          
    pygame.display.flip()
    horloge.tick(images_par_seconde)
    

  
    