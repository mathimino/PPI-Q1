#BECKERS Mathias
#PIRICK Arthur
#https://github.com/mathimino/PPI-Q1

import math
import pygame
import random

#Couleur

NOIR = (0, 0, 0)
JAUNE = (255, 255, 0)
ROUGE = (255,0,0)
ORANGE = (255,165,0)
BLEU = (0,0,255)
WHITE = (255, 255, 255)
couleur_fond = NOIR

# Vaisseau

RAYON_VAISSEAU = 20
VITESSE_MISSILE_INIT = 0.7

#planete , etoiles

RAYON_PLANETE_MIN=100
RAYON_PLANETE_MAX=300
DIST_MIN_ENTRE_PLANETE = 400
NBR_PLANETE_MIN = 750
NBR_PLANETE_MAX=1000
NOMBRE_ETOILES = 10000

#gravité

RAYON_INFLUENCE = 1000
CONSTANTE_GRAV = 0.0001
FACTEUR_GRAVITE_MISSILE = 3

#stats joeurs

global nombre_vies
nombre_vies = 3
NOMBRE_VIES_INIT=3
global highscore
highscore = 0
global score
score = 0
global nouveau_meilleur_score
nouveau_meilleur_score = False

# Paramètres jeu,menu

dimensions_fenetre = (900,900)  # en pixels
DISTANCE_AFFICHAGE = 9*dimensions_fenetre[0]**2
LIMITES_JEU = [10000,10000]
images_par_seconde = 25
global enjeu
enjeu = False
global debug
debug = False
global quitte 
quitte = False





#variables missiles
temps_avant_recharge = 0
delai_recharge = 200

#entite
global scene

# player variables
x_player_ecran,y_player_ecran = dimensions_fenetre[0]/2,dimensions_fenetre[1]/2
position_player = x_player_ecran,y_player_ecran
orientation_player = 0
puissance_player = 1
masse_player = 3000
player_avance = False
vitesse_max_player = 1
distance_bord_ecran_x = abs(x_player_ecran+RAYON_VAISSEAU)
distance_bord_ecran_y = abs(y_player_ecran+RAYON_VAISSEAU)

#Ennemis
CPT_REVERSE = 50
CPT_SHOT = 25
VITESSE_MAX_ENNEMIS = 0.2
DISTANCE_REVERSE_PLANETE = 200
DISTANCE2_AVANCE_ENNEMIS = 90000 #400**2
FORCE_ENNEMIS = 0.3
global dernier_spawn_ennemi
dernier_spawn_ennemi = 0
NBR_ENNEMIS_MAX = 10
TEMPS_SPAWN_ENNEMIS_MIN = 2
ennemis_images = ["ship_avance.png","ship_stop.png"]
DUREE_VIE_ENNEMIS = 120

# Initialisation

pygame.init()
pygame.mixer.init()

fenetre = pygame.display.set_mode(dimensions_fenetre)
pygame.display.set_caption("Space Invaders 2D")
horloge = pygame.time.Clock()

musique = pygame.mixer.Sound("sons/musique_fond.wav")
musique.play(loops=-1)

police = pygame.font.SysFont('monospace', dimensions_fenetre[1]//50, True)
#cration de toutes les listes
scene ={
    "etoiles":[],
    "planetes" : [],
    "entites" : [],
    "missiles":[],
    "player":[],
    "ennemis":[]
}

#ajout des images de planetes aux listes
planetes_images = []
list_planetes_images = ["jupiter.png","mars.png","mercure.png","neptune.png","saturne.png","terre.png","uranus.png","venus.png"]
for image_planete in list_planetes_images:
    planetes_images.append(pygame.image.load('images/planetes/' + image_planete).convert_alpha(fenetre))

#ajout des images d explosion auux listes
explosion_images = []
explosion_nom_poses = ["explosion_1","explosion_2","explosion_3"]
for nom_fichier in explosion_nom_poses:
    image_explosion = pygame.image.load('images/explosion/'+nom_fichier + ".png").convert_alpha(fenetre)
    image_explosion = pygame.transform.scale(image_explosion,(RAYON_VAISSEAU,RAYON_VAISSEAU))
    explosion_images.append(image_explosion)

#on ajoute aux missiles ses images de mort et sa texture
missile_images = explosion_images
image_missile = pygame.image.load("images/missile/missile.png").convert_alpha(fenetre)
image_missile = pygame.transform.scale(image_missile,(RAYON_VAISSEAU,RAYON_VAISSEAU))
missile_images.append(image_missile)

#on load toutes les images pour le menu et on redimensionne
images_menu = pygame.image.load('images/menu/menu_fond.png').convert_alpha(fenetre)
images_menu = pygame.transform.scale(images_menu,(dimensions_fenetre[0],dimensions_fenetre[1]))
image_titre = pygame.image.load('images/menu/menu_titre.png').convert_alpha(fenetre)
image_titre= pygame.transform.scale(image_titre,(dimensions_fenetre[0],dimensions_fenetre[1]/2))
image_coeur = pygame.image.load('images/menu/vie_joueur.png').convert_alpha(fenetre)
image_coeur= pygame.transform.scale(image_coeur,(dimensions_fenetre[0]/10,dimensions_fenetre[0]/10))

# Fonctions generale animation
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

#creation de l animation de mort des entite
def cree_anim_mort():
    #on ajoute les mouvement a l animation
    animation_mort = nouvelleAnimation()
    ajouteMouvement(animation_mort,mouvement('explosion_1',200))
    ajouteMouvement(animation_mort,mouvement('explosion_2',200))
    ajouteMouvement(animation_mort,mouvement('explosion_3',500))
    return animation_mort

#gerer l animation de mort
def animation_mort_globale(entite,scene):
    global enjeu,nombre_vies
    if entite['animationActuelle']!=None:
                        animationActuelle = entite['animationActuelle']
                        poseActuelle = mouvementActuel(animationActuelle)
                        anime(animationActuelle)
                        nouvellePose = mouvementActuel(animationActuelle)
                        if nouvellePose == None:
                            entite['animationActuelle'] = None
                            if entite["type"]== "player":
                                #si l entite est le vaissseauu du joeur
                                #on eleve une vie
                                nombre_vies -=1
                                enjeu = False
                            #on detruit l entite qui n as plus de pose
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
     'rect': None,
     'temps_spawn':pygame.time.get_ticks(),
     'tireur':""
    }

def destroy_entite(scene,entite):
    if entite in scene:
        scene.remove(entite)

def ajouteEntite(scene, entite):
    scene.append(entite)

#fonction qui redimensionne la taille de l explosion en fonction de l entite    
def explosion_taille(entite,facteur_explosion):
    explosion_taille =entite["rayon"]*2*facteur_explosion
    explosion_enti_1 = pygame.transform.scale(explosion_images[0],(explosion_taille,explosion_taille))
    explosion_enti_2 = pygame.transform.scale(explosion_images[1],(explosion_taille,explosion_taille))
    explosion_enti_3 = pygame.transform.scale(explosion_images[2],(explosion_taille,explosion_taille))
    ajoute_pose(entite, "explosion_1", explosion_enti_1)
    ajoute_pose(entite, "explosion_2", explosion_enti_2)
    ajoute_pose(entite, "explosion_3", explosion_enti_3)

#fonction vaisseau
def cree_vaisseau():
    global player
    player_images =['player_avance.png','player_stop.png']
    #on cree le vaisseau
    player = nouvelle_entite('player',[x_player_ecran,y_player_ecran],RAYON_VAISSEAU,masse_player,None,orientation_player,0,0) #player["position"] est la position fixe à l'écran
    #on lui ajoute les poses du moteur
    for image in player_images:
        loaded_image = pygame.image.load('images/player/' + image).convert_alpha(fenetre)
        loaded_image = pygame.transform.scale(loaded_image,(RAYON_VAISSEAU*2,RAYON_VAISSEAU))
        ajoute_pose(player,image.replace(".png", ""),loaded_image)
    #on redimensionne ses imaages de mort
    explosion_taille(player,2)
    #on lui donne la posse vaisseau eteint
    prends_pose(player,"player_stop")
    #on ajoute l entite a la scene et on lui donne son animation de fin
    ajouteEntite(scene["player"],player)
    ajouteAnimation(player,"animation_mort",cree_anim_mort())
    return 

def allume_moteur(player_avance):
    #donne la pose avec flamme au vaisseau
    if player_avance==False:
        player_avance = True
        prends_pose(player,"player_avance")
    return player_avance

def eteint_moteur(player_avance):
    #on redonne la pose intiale au vaisseau
    player_avance = False
    prends_pose(player,"player_stop")
    return player_avance

def stop_vaisseau(vaisseau):
    #on stoppe entierement le vaisseau (DEBUG)
    get_delta_pos(vaisseau,pygame.time.get_ticks(),0,orientation_player,True)

def nouvelle_orientation_vaisseau_player():
        global orientation_player
    #on recupere la position du curseur
        mouse_x,mouse_y = pygame.mouse.get_pos()
        delta_mouse_x, delta_mouse_y = mouse_x-x_player_ecran, mouse_y-y_player_ecran
        
        # Calcul du nouvel angle du vaisseau par rapport à la position de la souris (modulo 360)
        if not estEnAnimation(player):
            angle_rad = math.atan2(delta_mouse_y,delta_mouse_x)
            orientation_player = (math.degrees(angle_rad))%360
            player["orientation"] = orientation_player
#fonction de deplacement
def get_delta_pos(entite,temps_maintenant,force_entite,orientation,stop=False):
    
    global position_player
    #cette fonction permet de calculer le deplacement de toute les entites en fonction du vaisseau
    #cordonnés du player dans la map
    x0,y0 = entite["position"]
    if entite["type"] == "player":
        x0,y0 = position_player
        

    vx0, vy0 = entite["vitesse_x_avant"], entite["vitesse_y_avant"]
    #on calcule le delta temps propre a chaque entite
    delta_t = temps_maintenant - entite["temps_avant"]
    
    #on prend l orientation dans l espace de  l entite
    angle_rad = math.radians(orientation)
    #récupération de l'accélération du player
    a = force_entite/entite["masse"]
    #on recupere les composante du vecteur acceleration
    ax = a*math.cos(angle_rad)
    ay = a*math.sin(angle_rad)
            

    # calcul gravité pour chaque planete ( dans le rayon d influence)
    a_planete_x,a_planete_y = calcul_gravite_planete(entite)
    #incrementation
    ax+=a_planete_x
    ay+=a_planete_y

    #mise a jour vitesse
    vx = vx0+ax*delta_t
    vy = vy0+ay*delta_t

    # Vitesse max
    #on bride la vitesse de l entite
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


    #mise a jour position de l entite
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
    #pour deplacer les entite et donc garder le joeur centrer
    return [x0-x,y0-y]

def calcul_gravite_planete(entite):
    #on applique la gravite uniquement aux missiles et au player
    if entite["type"] !="player" and entite["type"] !="missile": 
        return 0,0
    else:
        a_planete_x = 0
        a_planete_y = 0
        masse_entite = entite["masse"]
        x_entite,y_entite = entite["position"]
        #on enumere chaque planete dans scene
        for planete in scene['planetes']: 
                    x_planete,y_planete = planete["position"]

                    #distance au carré entre le player et la planete choisie
                    delta_x = x_planete-x_entite
                    delta_y = y_planete-y_entite
                    r2 = delta_x**2 + delta_y**2

                    #on applique la gravité pour un rayon appartenant à [0,rayon_influence]
                    #car apres ce rayon d influence : gravite negligeable
                    if r2<= RAYON_INFLUENCE**2 and r2>0:
                        r = math.sqrt(r2)
                        masse_planete = planete["masse"]

                        #calcul acceleration gravité
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

#generation des planetes          
def generer_carte():
    # Choix du nbr de planetes à créer
    nb_planetes=random.randint(NBR_PLANETE_MIN,NBR_PLANETE_MAX)
    for planetes in range(nb_planetes):
        # Génération de la position du la nouvelle planete
        x_gen_planete = random.randint(-LIMITES_JEU[0],LIMITES_JEU[0])
        y_gen_planete = random.randint(-LIMITES_JEU[1],LIMITES_JEU[1])
        #on  calcule la distance entre la planete et le spawn
        delta_x = x_gen_planete - position_player[0]
        delta_y = y_gen_planete -position_player[1]
        dist_spawn2 = delta_x**2 + delta_y**2
        #on choisit une taille aleatoire pour la planete
        rayon = random.randint(RAYON_PLANETE_MIN,RAYON_PLANETE_MAX)
        
        #Si la nouvelle planete est au moins à une certaine distance du spawn du vaisseau
        if dist_spawn2 >= (rayon+(dimensions_fenetre[0]+dimensions_fenetre[1])/4)**2:
            #une planete plus grande est plus massive
            masse = rayon*rayon*3
            #on donne une image aleatoire à la planete
            choix_images_planete = random.choice(planetes_images)
            #on la redimensionne en fonction du rayon
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
                #on cree la planete et on l ajoute a la scene
                planete = nouvelle_entite("planete",[x_gen_planete,y_gen_planete],rayon,masse,photo_planete)
                ajouteEntite(scene["planetes"],planete)

#generation des etoiles
def generer_fond_etoile():
    #on cree un nombre d image aleatoire
    for etoiles in range (NOMBRE_ETOILES):
        #on les genere a une position aleatoire dans les limites de la map
        x_gen_etoiles = random.randint(-LIMITES_JEU[0],LIMITES_JEU[0])
        y_gen_etoiles = random.randint(-LIMITES_JEU[1],LIMITES_JEU[1])
        #on cree l etoile et on l ajoute a la scene
        etoile = nouvelle_etoile([x_gen_etoiles,y_gen_etoiles])
        ajouteEntite(scene["etoiles"], etoile)

#fonctions d'affichage

def afficher_planete(planete):
    #on recupere l image de la planete
    photo_planete = planete['image']
    #on recupere sa position par rapport au centre de son rectangle(=image)
    position = photo_planete.get_rect(center =(planete["position"]))
    #on l affiche aux coordonné calculé
    fenetre.blit(photo_planete,position)
    return

def afficher_vaisseau(vaisseau):
    #si le vaisseau est un player 
    x,y = vaisseau["position"]
    if vaisseau["type"] == "player":
        x,y = x_player_ecran,y_player_ecran
    # on verifie que l ennemi n est pas en animation (pour ne pas la casser)
    if vaisseau["type"] == "ennemi" and not estEnAnimation(vaisseau):
        if vaisseau["avance"]:
            prends_pose(vaisseau,"ship_avance")
        else:
            prends_pose(vaisseau,"ship_stop")
    
      #Il faut rajouter un moins sinon l'image du vaisseau tourne dans le mauvais sens
      # (pygame.rotate pas dans le sens trigono)
    photo_vaisseau_r = pygame.transform.rotate(vaisseau["image"],-vaisseau["orientation"])
    #on calcule la nouvelle hit box du vaisseau apres la rotation d image
    vaisseau["rect"]= photo_vaisseau_r.get_rect(center = (x,y))
    #on l affiche aux coordone du centre du rect
    fenetre.blit(photo_vaisseau_r,vaisseau["rect"])
    #si en mode DEBUG , on affiche la HIT BOX
    if debug:
        pygame.draw.rect(fenetre, ROUGE, vaisseau["rect"], 1)

def afficher_missile(missile):
    #on recupere l image du missile
    image_missile = missile["image"]
    if missile["type"] == "missile":
        x,y = missile["position"]

    #Il faut rajouter un moins sinon l'image du vaisseau tourne dans le mauvais sens
    #meme chose que pour le vaisseau
    image_missile = pygame.transform.rotate(missile["image"],-missile["orientation"])
    #on recupere la nouvelle HIT BOX , apres rotation
    missile["rect"] = image_missile.get_rect(center = (x,y))
    #on affiche  aux coordone du centre du rect
    fenetre.blit(image_missile,missile["rect"])
    #si en mode DEBUG , on affiche la HITBOX
    if debug:
        pygame.draw.rect(fenetre, ROUGE, missile["rect"], 1)
    
    return   

def afficher_menu():
    global nombre_vies,highscore,score,nouveau_meilleur_score

    #on affiche le fond ainsi que le logo SPACE INVADERS
    fenetre.fill(couleur_fond)
    fenetre.blit(images_menu,(0,0))
    fenetre.blit(image_titre,(10,50))
    temps_titre = pygame.time.get_ticks()
    
    #si le nouveau score est superieur , on update le meuilleur score
    if score >highscore:
        highscore = score
        nouveau_meilleur_score = True
        
    
    #on centre le texte du meuilleur score au centre haut de l ecran
    texte_meilleur_score = police.render(("HIGHSCORE :"+str(highscore)),True,JAUNE)
    texte_score= police.render(("TON SCORE :"+str(score)),True,WHITE)
    texte_meilleur_score_coord = texte_meilleur_score.get_rect(center=(dimensions_fenetre[0]/2,2*dimensions_fenetre[1]/30))
    texte_score_coord = texte_score.get_rect(center=(dimensions_fenetre[0]/2,dimensions_fenetre[1]/30))
    texte_quitter = police.render(("Appuyez sur [esc] pour quitter"),True , ROUGE)
    texte_quitter = pygame.transform.scale(texte_quitter,(4*dimensions_fenetre[0]/5,dimensions_fenetre[1]/15))
    #si on a encore des vies
    if not quitte:
        if nombre_vies>0:
            #on fait clignoter le texte COMMENCE et le texte record battu
            if (temps_titre//1000)%3!=0:
                if nouveau_meilleur_score:
                    texte_nouveau_record = police.render(("RECORD BATTU!!"),True,ROUGE)
                    texte_nouveau_record_coord = texte_nouveau_record.get_rect(center=(dimensions_fenetre[0]/2,2*dimensions_fenetre[1]/30))
                    texte_nouveau_record_coord = texte_nouveau_record.get_rect(center=(texte_meilleur_score_coord[0]-texte_nouveau_record_coord[2]/2-20,dimensions_fenetre[1]/15))
                    fenetre.blit(texte_nouveau_record,texte_nouveau_record_coord)
                commenceJouer= police.render(("Appuyez sur [espace] pour commencer"), True, JAUNE)
                commenceJouer = pygame.transform.scale(commenceJouer,(2*dimensions_fenetre[0]/3,dimensions_fenetre[1]/14))
                fenetre.blit(commenceJouer,(dimensions_fenetre[0]/6,300))
                texte_quitter_cord = texte_quitter.get_rect(center = (dimensions_fenetre[0]/2,3.5*dimensions_fenetre[1]/5))
                fenetre.blit(texte_quitter,texte_quitter_cord) 
            #on affiche les raccourcis
            text_controls = police.render(("Controler le vaisseau avec [Z] et le curseur de souris"), True, WHITE)
            text_controls = pygame.transform.scale(text_controls,(9*dimensions_fenetre[0]/10,dimensions_fenetre[1]/17))
            fenetre.blit(text_controls,(dimensions_fenetre[0]/20,400))
            
            text_shoot = police.render(("Tirez avec un clic de la souris ou [T]"), True, WHITE)
            text_shoot = pygame.transform.scale(text_shoot,(4*dimensions_fenetre[0]/5,dimensions_fenetre[1]/17))
            fenetre.blit(text_shoot,(dimensions_fenetre[0]/10,500))

        
            #on affiche le nombre de vie centrée
            for i in range(nombre_vies):
                fenetre.blit(image_coeur,(dimensions_fenetre[0]/2-(nombre_vies/2)*dimensions_fenetre[0]/10+i*dimensions_fenetre[0]/10,dimensions_fenetre[1]-200))

        #si on a plus de vie        
        if nombre_vies <=0:
            if (temps_titre//1000)%3!=0:
                if nouveau_meilleur_score:
                    texte_nouveau_record = police.render(("RECORD BATTU!!"),True,ROUGE)
                    texte_nouveau_record_coord = texte_nouveau_record.get_rect(center=(dimensions_fenetre[0]/2-150,2*dimensions_fenetre[1]/30))
                    fenetre.blit(texte_nouveau_record,texte_nouveau_record_coord)
                texte_ecran_titre = police.render(("Appuyez sur [espace] pour revenir à l'écran titre ! "),True,JAUNE)
                texte_ecran_titre= pygame.transform.scale(texte_ecran_titre,(dimensions_fenetre[0]/2,dimensions_fenetre[1]/15))
                texte_ecran_titre_coord = texte_ecran_titre.get_rect(center = (dimensions_fenetre[0]/2,3*dimensions_fenetre[1]/5))
                fenetre.blit(texte_ecran_titre,texte_ecran_titre_coord)
                texte_quitter_cord = texte_quitter.get_rect(center = (dimensions_fenetre[0]/2,3.5*dimensions_fenetre[1]/5))
                fenetre.blit(texte_quitter,texte_quitter_cord) 
                
            texte_game_over = police.render(("GAME OVER"),True , ROUGE)
            texte_game_over = pygame.transform.scale(texte_game_over,(4*dimensions_fenetre[0]/5,dimensions_fenetre[1]/15))
            fenetre.blit(texte_game_over,(dimensions_fenetre[0]/10,dimensions_fenetre[1]/2))
        
        
        #on affiche le score apres la premiere partie
        if nombre_vies<NOMBRE_VIES_INIT:
                fenetre.blit(texte_meilleur_score,texte_meilleur_score_coord)
                fenetre.blit(texte_score,texte_score_coord)
    #si on quitte le jeu
    else :
        texte_fin = police.render(("Merci d'avoir jouer! A bientôt !"),True ,WHITE)
        texte_fin = pygame.transform.scale(texte_fin,(dimensions_fenetre[0]/2,dimensions_fenetre[1]/15))
        texte_fin_coord = texte_fin.get_rect(center = (dimensions_fenetre[0]/2,dimensions_fenetre[1]/2))
        fenetre.blit(texte_fin,texte_fin_coord)

        
    
            
def affiche(scene,delta_pos):
    #on ennumere chaque entite dans scene
    for key in scene.keys():
        for entite in scene[key]:
            
            
            if key == "player":
                #si l entite est le vaisseau , on l affiche
                #si il est mort , on anime
                afficher_vaisseau(player)
                animation_mort_globale(entite,scene["player"])
            else:
                #on deplace chaque entite par rapport au vaisseau
                entite["position"][0] += delta_pos[0]
                entite["position"][1] += delta_pos[1]
                rayon = 0
                #on verifie que l entite a bien un rayon
                if "rayon" in entite:
                    rayon = entite["rayon"]
                #on anime chaque entite (SI il sont mort , puis on les detruit)
                if key =="missiles":
                    afficher_missile(entite)
                    animation_mort_globale(entite,scene["missiles"])
                    
                if key =="ennemis":
                    afficher_vaisseau(entite)
                    animation_mort_globale(entite,scene["ennemis"])
                    
                    
            #on calcule la distance de l'entite par rapport au centre de l ecran
            distance_entite_x = abs(entite["position"][0] - x_player_ecran)-rayon
            distance_entite_y = abs(entite["position"][1] - y_player_ecran) - rayon
            #si l entite est dans la fenetre alors on l affiche
            if distance_entite_x <= distance_bord_ecran_x and distance_entite_y <= distance_bord_ecran_y:
                if key == "planetes":
                    afficher_planete(entite)
                elif key == "etoiles":
                    #pour chaque etoile , on dessine un cercle blanc
                    pygame.draw.circle(fenetre,WHITE,(entite["position"][0],entite["position"][1]),1)
            

    #si on est en mode DEBUG on affiche les donnés du vaisseau 
    if debug:
        afficher_text_debug()

    #on centre le score en haut de l ecran puis on l affiche                   
    texte_score = police.render("score: "+str(score),True , WHITE)
    texte_score_coord = texte_score.get_rect(center=(dimensions_fenetre[0]/2,dimensions_fenetre[1]/30))
    fenetre.blit(texte_score ,texte_score_coord)
 
def afficher_text_debug():
    #Ne s affiche que si le mode DEBUG est activé

    #affiche la position du vaisseau
    coord_txt= police.render("X:" + str(round(position_player[0])) + ",Y:" + str(round(position_player[1])), True, WHITE)
    fenetre.blit(coord_txt, (0,0))
    
    #affiche son orientation
    angle_txt= police.render("Angle:" + str(round(orientation_player,2)) + " deg", True, WHITE)
    fenetre.blit(angle_txt, (0,15))

    #affiche ses vitesses
    vx_txt= police.render("Vitesse X:" + str(round(player["vitesse_x"],2)), True, WHITE)
    fenetre.blit(vx_txt, (0,30))
    vy_txt= police.render("Vitesse Y:" + str(round(player["vitesse_y"],2)), True, WHITE)
    fenetre.blit(vy_txt, (0,45))

#fonctions missiles

def tir_cannon(entite):
    #permet aux entite de tirer des missiles

    #on verifie que l entite n a pas exploser
    if not  estEnAnimation(entite):
        global temps_avant_recharge
        temps_maintenant = pygame.time.get_ticks()
        delai = temps_maintenant-temps_avant_recharge
        
        #on evite a l entite de pouvoir tirer des missiles trop souvent
        if delai > delai_recharge:

            #on recupere l orientation de l entite au moment ou elle tire
            orientation_missile = entite["orientation"]

            #on recupere sa position
            x,y= entite["position"]
            if entite["type"] == "player":
                x,y = x_player_ecran,y_player_ecran 

            #si le delai est respecte on permet le tir et on cree l entite
            #on lui donne un delai de vie  pour l autodestruction (=200 ticks ~9sec)
            missile = nouvelle_entite('missile',[x,y],RAYON_VAISSEAU/2,1000,None,orientation_missile,0,0,900,200)

            #on dit au missiles par qui il a ete tiré
            missile["tireur"]= entite["type"]

            #on transforme l'orientation en radian
            angle_rad_missile = math.radians(orientation_missile)

            #on additionne la vitesse du missile a la vitesse de l entite
            # (pour quele missile aille plus vite que l entite)
            missile['vitesse_x'] = entite["vitesse_x"] + VITESSE_MISSILE_INIT*math.cos(angle_rad_missile)
            missile['vitesse_y'] = entite["vitesse_y"] + VITESSE_MISSILE_INIT*math.sin(angle_rad_missile)

            #on lui donne les poses de mort 
            for index,item in enumerate(explosion_nom_poses):
                ajoute_pose(missile,item,explosion_images[index])

            #on lui donne sa pose initiale ( la texture du missile)
            ajoute_pose(missile,"missile",missile_images[len(missile_images)-1])
            prends_pose(missile,'missile')

            #on ajoute le missile a la scene et on lui donne l animation de mort
            ajouteEntite(scene["missiles"],missile)
            explosion_taille(missile,2)
            ajouteAnimation(missile,'animation_mort',cree_anim_mort())

            #on reinitialise son temp de recharge ( pour un nouveau delai)
            temps_avant_recharge = temps_maintenant
    return

def autodestruction_missile(missile):
    #on recupere le temps restant du missile
    delai_vie  = missile["duree_vie"]
    
    #si il ne reste plus de temps au missiles , il sautodetruit, et commence l animation de mort
    #on verifie egalement que ce missile n est pas deja mort
    if (delai_vie<=0 and not estEnAnimation(missile)) :
            commenceAnimation(missile,'animation_mort',1)
    return

def mise_a_jour_etat_missile(delta_t):
    #on enumere chaque missile dans la scene
    for missile in scene['missiles']:

        #on les empeche de bouger si il sont mort
        if not estEnAnimation(missile):

            # on calcule leur vecteur acceleration
            a_planete_x , a_planete_y = calcul_gravite_planete(missile)

            #on les deplace par rapport a leur vitesse (en plus de delta pos )
            missile["vitesse_x"]+=a_planete_x*delta_t*FACTEUR_GRAVITE_MISSILE
            missile["vitesse_y"]+=a_planete_y*delta_t*FACTEUR_GRAVITE_MISSILE

            missile["position"][0]+=missile["vitesse_x"]*delta_t
            missile["position"][1]+=missile["vitesse_y"]*delta_t
            missile["duree_vie"]-=1
            
            #on gere leurs collision avec les planetes
            collision_planetes(missile)

            #on verifie qu il peuvent encore etre en vie
            autodestruction_missile(missile)

def calcul_delta_t():
    global dernier_temps_missiles
    #calcul du delta_temps pour la mise a jour position
    temps_maintenant = pygame.time.get_ticks()
    delta_t_missile = temps_maintenant-dernier_temps_missiles
    dernier_temps_missiles = pygame.time.get_ticks()
    return delta_t_missile
#fonctions collisions

def collision_planetes(entite):
    global scene
    #on recupere la position de l entite
    xp,yp = entite["position"]
    index_planete_proche = 0
    min_dist = float(math.inf)

    #on parcours toutes les planetes et on recupere leurs position
    for index, planete in enumerate(scene["planetes"]):
        x_planete , y_planete = planete["position"]

        #on calcule la distance entre l entite et la planete
        delta_x = x_planete-xp
        delta_y = y_planete-yp

        #distance au carré entre la planete et l'entite
        r2 = delta_x**2 + delta_y**2

        #detection de la distance pour collision
        rayon_total = planete["rayon"]+RAYON_VAISSEAU

        #si l entite est un ennemi ( cette partie est utilisé pour son IA)
        if entite["type"] == "ennemi":

            # On cherche la planete la plus proche de l'ennemi
            #la distance entre le bord de la planete et le bord de l'entite

            distance_planete = abs(math.sqrt(r2)-rayon_total)
            if distance_planete < min_dist and distance_planete>0:
                min_dist = distance_planete
                index_planete_proche = index
            
            #si la collision est detecté et que l ennemi n est pas deja mort
            if r2 <= rayon_total**2 and not estEnAnimation(entite):
                commenceAnimation(entite,"animation_mort",1)

        #si l'entite est un missile ou le vaisseau joeur , que la collision est detecté et qu il n est pas deja mort
        if (entite["type"] == "player" or entite["type"] == "missile") and r2 <= rayon_total**2 and not estEnAnimation(entite):
            commenceAnimation(entite,"animation_mort",1)

    # on retourne l'index de la planete la plus proche de l'ennemi(Pour IA ennemi)
    return index_planete_proche
    
def collision_missiles():
    global score
    # pour chaque missile
    temps_maintenant = pygame.time.get_ticks()
    for missile in scene["missiles"]:
        # on parcour chaque entite sauf les étoiles et les planetes
        for key in scene.keys():
            if key != "etoiles" and key != "planetes":
                for entite in scene[key]:

                    # si le missile existe depuis asser longtemps pour ne pas tuer l'entite qui le lance 
                    # et si on ne compare pas le missile avec lui même 
                    # et si l'entité et le missile se superpose 
                    # et si le missile et l'entité ne sont pas en animation
    
                    if temps_maintenant-missile["temps_spawn"]>=200 and missile["temps_spawn"]!=entite["temps_spawn"] \
                        and missile["rect"].colliderect(entite["rect"]) and not estEnAnimation(missile) and not estEnAnimation(entite):

                        #si deux missiles se detruisent entre eux
                        if entite["type"] == "player":
                            stop_vaisseau(player)
                        if entite["type"] == "missile":

                            commenceAnimation(missile,"animation_mort",1)

                        #si la collision est entre un missile et une autre entite(l explosition ne sera que pour l entite)
                        else:
                            destroy_entite(scene["missiles"],missile)
                        commenceAnimation(entite,"animation_mort",1)

                        #si un ennemi est tué , et que le missile a ete tiré par le joeur , on augmente le score
                        if entite["type"] == "ennemi" and missile["tireur"]=="player":
                            score =score+1000

def collision_vaisseaux():
    #collsion entre deux vaisseau ennemis
    for vaisseau in scene["ennemis"]:
        for ennemi in scene["ennemis"]:
            #si on ne compare pas le vaisseau avec lui meme(eviter qu il se detruise direct)
            #on verifie que il ne sont pas deja mort
            if vaisseau["rect"].colliderect(ennemi["rect"]) and vaisseau["temps_spawn"] != ennemi["temps_spawn"] \
                and not estEnAnimation(vaisseau) and not estEnAnimation(ennemi):
                commenceAnimation(vaisseau,"animation_mort",1)
                commenceAnimation(ennemi,"animation_mort",1)
        #collision entre le joeur et les ennemis
        #on verifie egalement que les entites ne sont pas deja mortes
        if player["rect"].colliderect(vaisseau["rect"]) and not estEnAnimation(player) and not estEnAnimation(vaisseau):
                commenceAnimation(player,"animation_mort",1)
                commenceAnimation(vaisseau,"animation_mort",1)

#fonctions (autres)

def gerer_touche(event):
    global player_avance
    global enjeu
    global dernier_temps_missiles
    global debug
    global score
    global nouveau_meilleur_score
    global highscore
    global nombre_vies
    global quitte
    
    #si on appuie sur la croix
    if event.type == pygame.QUIT or(event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            quitte = True

    if event.type == pygame.QUIT:
            musique.stop()  
            pygame.display.quit()
            pygame.quit()
            exit()

    #si clic souris et en jeu
    if event.type == pygame.MOUSEBUTTONDOWN and enjeu:
        tir_cannon(player)
    #si on est deja en jeu
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
                    case pygame.K_n:
                        stop_vaisseau(player)
                    case pygame.K_t :
                        tir_cannon(player)
                        
                    

                    #autodestruction du vaisseau
                    case pygame.K_o:
                        commenceAnimation(player,"animation_mort",1)

                    #activation mode debug
                    case pygame.K_a:
                        if debug:
                            debug = False
                        elif debug == False:
                            debug = True
    
    #on appuie sur espace pour commencer le jeu
    elif not enjeu and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
        if nombre_vies<=0:
            nombre_vies = 3
            score = 0
            highscore = 0
            nouveau_meilleur_score = False
        else:
            reset_jeu()
            enjeu = True
            nouveau_meilleur_score = False
            score = 0
            temps_reset =pygame.time.get_ticks()
            

            #avant de reccomencer , on reset tout les temps a 0
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

    #si on est en mode DEBUG , on affiche le rayon de retournement du vaisseau, 
    # la ligne entre le vaisseau et la planete et la ligne entre le vaisseau et le joueur
    if debug:
        # dessin des aides visuelles pour l'ia
        pygame.draw.circle(fenetre, ROUGE, planete["position"],rayon_total+DISTANCE_REVERSE_PLANETE, 3)
        
        pygame.draw.line(fenetre,(0,255,0),ennemi["position"],planete["position"], 3)
        if distance2_player >= DISTANCE2_AVANCE_ENNEMIS:
            pygame.draw.line(fenetre,(138,43,226),ennemi["position"],[x_player_ecran,y_player_ecran], 3)
        else:
            pygame.draw.line(fenetre,ORANGE,ennemi["position"],[x_player_ecran,y_player_ecran], 3)

    #la force des ennemis , est la force du moteur
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
        force_ennemi= 1
        ennemi["cpt_reverse"] -= 1
        ennemi["avance"] = True

    
    #timer pour savoir si on peux tirer de nouveau
    if ennemi["cpt_shot"] >= 0:
        ennemi["cpt_shot"]-=1

    if ennemi["cpt_shot"] == -1:
        ennemi["cpt_shot"]= CPT_SHOT
        # Quanf le timer est fini, on a 50% de chance de tirer
        can_shoot = random.randint(1,2)
        if can_shoot == 1 :
            tir_cannon(ennemi)


    ennemi["orientation"] = orientation_ennemi
    #on calcule son deplacement independant du joueur , et on l applique
    delta_pos = get_delta_pos(ennemi,pygame.time.get_ticks(),force_ennemi,orientation_ennemi)
    ennemi["position"][0] -= delta_pos[0]
    ennemi["position"][1] -= delta_pos[1]

#a corriger un peu bizarre
def spawn_enemis():
    global dernier_spawn_ennemi

    # on determine le nombre d ennemi deja present dans la scene
    nbr_ennemis = len(scene["ennemis"])+1

    spawn_random = random.randint(1,20)
    spawn_time = pygame.time.get_ticks()//1000 #en secondes piles

    #on a une chance sur 20 de faire spawn un ennemi a chaque iteration si:
    #le mob cap n est pas atteint
    #que l on a pas deja spawn un ennemi 
    if nbr_ennemis<=NBR_ENNEMIS_MAX and dernier_spawn_ennemi!=spawn_time and spawn_random==1 and (spawn_time%TEMPS_SPAWN_ENNEMIS_MIN)==0:
        dernier_spawn_ennemi = spawn_time

        
        x=0
        y=0
        cote = 0

        #on choisit le cote ou l ennemi spawn et on choisit une coordoné
        match random.randint(1,4):
            case 1:
                #Côté haut
                cote = 1
                x = random.randint(0,dimensions_fenetre[0])
                y = -(RAYON_VAISSEAU*3)
            case 2:
                #Côté droit
                cote = 2
                x = dimensions_fenetre[0] + RAYON_VAISSEAU*3
                y = random.randint(0,dimensions_fenetre[1])
            case 3:
                #Côté bas
                cote = 3
                x = random.randint(0,dimensions_fenetre[0])
                y = dimensions_fenetre[1] + RAYON_VAISSEAU*3
            case 4:
                #Côté gauche
                cote = 4
                x = -(RAYON_VAISSEAU*3)
                y = random.randint(0,dimensions_fenetre[1])
         
        # on empeche a un ennemi de spawn sur une planete
        for planete in scene["planetes"]:
            delta_x = x-planete["position"][0] 
            delta_y = y-planete["position"][1]
            distance2_planete = delta_x**2 + delta_y**2
            if distance2_planete<= (planete["rayon"] + DISTANCE_REVERSE_PLANETE + RAYON_VAISSEAU)**2:
                if cote == 1 or cote == 3:
                    x += planete["rayon"] + DISTANCE_REVERSE_PLANETE + RAYON_VAISSEAU
                elif cote == 2 or cote == 4:
                    y += planete["rayon"] + DISTANCE_REVERSE_PLANETE + RAYON_VAISSEAU 

        #on cree l ennemi
        ennemi = nouvelle_entite("ennemi",[x,y],RAYON_VAISSEAU,3000,None,0.3,0,0,VITESSE_MAX_ENNEMIS,DUREE_VIE_ENNEMIS)
        
        #on lui donne ses images
        for image in ennemis_images:
            loaded_image = pygame.image.load('images/ennemis/' + image).convert_alpha(fenetre)
            loaded_image = pygame.transform.scale(loaded_image,(ennemi["rayon"]*2,ennemi["rayon"]*2))
            ajoute_pose(ennemi,image.replace(".png", ""),loaded_image)
        for index,item in enumerate(explosion_images):
                ajoute_pose(ennemi,item,explosion_images[index])
        prends_pose(ennemi,"ship_stop")

        #on lui donne son animation de mort,redimensionne son explosion, et l ajoute a la scene
        ajouteAnimation(ennemi,'animation_mort',cree_anim_mort())
        explosion_taille(ennemi,2)
        ajouteEntite(scene["ennemis"],ennemi)

def despawn_ennemis():
     #Supprime tous les ennemis qui ont été hors de l'écran pendant un certain temps
    for ennemi in scene["ennemis"]:
        # si l'ennemi est hors de l'écran
        if ennemi["position"][0] < 0 or ennemi["position"][0] > dimensions_fenetre[0] \
            or ennemi["position"][1] < 0 or ennemi["position"][1] > dimensions_fenetre[1]:
            ennemi["duree_vie"] -= 1
            if ennemi["duree_vie"] < 0:
                destroy_entite(scene["ennemis"],ennemi)
        else:
            ennemi["duree_vie"] = DUREE_VIE_ENNEMIS
#fin a corriger

def reset_jeu():
    #fonction de reset du jeu , apres chaque mort
    global enjeu
    global nombre_vies
    global highscore,score
    global position_player
    global player_avance
    enjeu = False
    global scene
    
    #on supprime toute les entite
    scene = {
    "etoiles":[],
    "planetes" : [],
    "entites" : [],
    "missiles":[],
    "player":[],
    "ennemis":[]
    }

    #on cree le vaisseau , et on reset ses variables 
    cree_vaisseau()
    player["position"]= dimensions_fenetre[0]/2,dimensions_fenetre[1]/2
    player["vitesse_x"]=0
    player["vitesse_y"]=0
    player["vitesse_x_avant"]=0
    player["vitesse_y_avant"]=0
    player["temps_avant"]=0
    player["orientation"]=0
    player_avance = False
    player["animationActuelle"]=None
    position_player = x_player_ecran,y_player_ecran

    #on genere une nouvelle map et un nouveau fond
    generer_carte()
    generer_fond_etoile()
    
    #si le nombre de vies vaut 0, on reset le score , le meuilleur score , et on redonne 3 vies
    if nombre_vies == 0:
        nombre_vies = NOMBRE_VIES_INIT
        highscore = 0
        score = 0
    return

#initialisation du jeu, on cree la map , le joueur etc

reset_jeu()

### Boucle de jeu ###
while True:
    for event in pygame.event.get():
            gerer_touche(event)

    #boucle principale
    if enjeu:
        pygame.key.set_repeat(10,10)
        delta_pos = [0,0]     
        
        #on gere les entite
        fenetre.fill(couleur_fond)
        nouvelle_orientation_vaisseau_player()
        spawn_enemis()
        despawn_ennemis()
        mise_a_jour_etat_missile(calcul_delta_t())

        for ennemi in scene["ennemis"]:
            if not estEnAnimation(ennemi):
                ai_ennemi(ennemi)

        if player_avance:
            force_player = puissance_player
        else:
            force_player = 0


        
        #on gere les deplacement
        if not estEnAnimation(player):
            delta_pos = get_delta_pos(player,pygame.time.get_ticks(),force_player,orientation_player)

        #on gere les collisions
        collision_planetes(player)
        collision_missiles()
        collision_vaisseaux()
        
        #on affiche le tout
        affiche(scene, delta_pos)

       
    if not enjeu:
        pygame.key.set_repeat(0,0)
        #on affiche l ecran d attente
        afficher_menu()
    if quitte:
        afficher_menu()
        pygame.display.flip()
        pygame.time.wait(5000)
        musique.stop()  
        pygame.display.quit()
        pygame.quit()
        exit()
    #on raffraichit l image
    pygame.display.flip()
    horloge.tick(images_par_seconde)