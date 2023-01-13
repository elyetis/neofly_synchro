# PLAN
- on verifie que NeoFly.exe ne tourne pas : :white_check_mark:
- on recupere dans ini date limite du dernier export : :white_check_mark:
- verifie les changement depuis le dernier export : :white_check_mark:
- si il y a eu des changement :
    - trie le nouvel export cree : :white_check_mark:
        - retirer lignes ou la description commence par 'user_import' pour ne pas exporter des imports : :construction:
    - renomme le csv : :white_check_mark:
    - upload du csv : :white_check_mark:
    - on enregistre/ecrase dans ini date limite de l'export qui viens d'être fait/dernier export : :white_check_mark:
    - conserver backup dans sous dossier : :mag:


- on recupere dans ini date limite du dernier import : :white_check_mark:
- on cherche dans github un ou plusieurs fichiers plus recent : :white_check_mark:
- si il y a des fichier plus recent : 
    - on telecharge les fichier : :white_check_mark:
    - modifier contenu description pour differencier joueurs : :white_check_mark:
    - modifier la date si difference fuseau horaire, valeur dans .ini ou genere dans noms des fichier csv : :white_check_mark:
    - insere le contenu des fichier dans db table "balances" : :white_check_mark:
    - calculer la difference incomes / expenses pour avoir la difference : :white_check_mark:
    - appliquer la difference dans la db, table : career, cash : :white_check_mark:
        - cas particulier ou 'cash' irai dans le negatif : :mag:
    - on enregistre/ecrase dans ini date limite de l'import qui viens d'être fait/dernier import : :white_check_mark:
    - supprimer les csv importés : :construction:

