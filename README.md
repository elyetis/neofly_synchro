# PLAN
- on recupere dans ini date limite du dernier export : *DONE*
- verifie les changement depuis le dernier export : *DONE*
- si il y a eu des changement : *DONE*
    - trie le nouvel export cree : *DONE*
    - renomme le csv : *DONE*
    - upload du csv : *DONE*
    - on enregistre/ecrase dans ini date limite de l'export qui viens d'être fait/dernier export : *DONE*


- on recupere dans ini date limite du dernier import : *DONE*
- on cherche dans github un ou plusieur fichier plus recent : *DONE*
- si il y a des fichier plus recent : *DONE*
    - on telecharge les fichier : *DONE*
    - (?) modifier contenu description pour differentier joueurs (?)
    - calculer la difference incomes / expenses pour avoir la difference
    - appliquer la difference dans la db, table : career, cash
        - cas particulier ou ca irai dans le negatif ? 
    - insere le contenu des fichier dans db table "balances"
    - on enregistre/ecrase dans ini date limite de l'import qui viens d'être fait/dernier import

