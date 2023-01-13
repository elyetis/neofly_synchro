# PLAN
- on recupere dans ini date limite du dernier export : *DONE*
- verifie les changement depuis le dernier export : *DONE*
- si il y a eu des changement :
    - trie le nouvel export cree : *DONE*
        - retirer lignes ou la description commence par 'user_import' pour ne pas exporter des imports
    - renomme le csv : *DONE*
    - upload du csv : *DONE*
    - on enregistre/ecrase dans ini date limite de l'export qui viens d'être fait/dernier export : *DONE*


- on recupere dans ini date limite du dernier import : *DONE*
- on cherche dans github un ou plusieurs fichiers plus recent : *DONE*
- si il y a des fichier plus recent : 
    - on telecharge les fichier : *DONE*
    - modifier contenu description pour differencier joueurs : *DONE*
    - modifier la date si difference fuseau horaire, valeur dans .ini ou genere dans noms des fichier csv : *DONE*
    - insere le contenu des fichier dans db table "balances" : *DONE*
    - calculer la difference incomes / expenses pour avoir la difference : *DONE*
    - appliquer la difference dans la db, table : career, cash : *DONE*
        - (?) cas particulier ou 'cash' irai dans le negatif (?)
    - on enregistre/ecrase dans ini date limite de l'import qui viens d'être fait/dernier import : *DONE*

