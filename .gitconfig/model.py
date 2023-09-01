import module, place, transition, note


NET_MARKER = "net"


class Model:

    # Sections
    transitions = "[]" # shared list between instances... so we initialize a fake variable
    places = "[]"
    notes = "[]"
    header = ""
    

    def __init__(self, file, tree, clash_frame):
        f = open(file, 'r')
        content = f.read()
        lines = content.split("\n")

        self.transitions = [] # avoid shared lists
        self.places = []
        self.notes = []
        self.tree = tree

        self.node = tree.insert("", "end", text=str(file), open=True)
        self.clash_frame= clash_frame

        n = len(lines)
        # Start from the end of the file so notes are handlesd first, then places then transitions
        # this is very important since there is a dependance link between these elements
        for k in range(n):
            line = lines[n-k-1]

            # We should encounter the lines desribing the notes first
            if note.is_note(line):
                nt = note.Note(line)
                self.notes.append(nt)

            # Create the place with associated description note in the list of notes
            if place.is_pl(line):
                pl = place.Place(line, self)
                self.add_place(pl)

            # Create the transition with associated places for arcs
            if transition.is_tran(line):
                tran = transition.Transition(line, self)
                self.add_tr(tran)

            # Header line
            if line.split(" ")[0] == NET_MARKER:
                self.header = line
            
        # Making all ids unique
        for pl in self.places:
            pl.name = module.make_unique(place.MARKER)
            pl.description.name = pl.name
            pl.update_view()
        for tr in self.transitions:
            tr.name = module.make_unique(transition.MARKER)
            tr.description.name = tr.name
            tr.update_view()
        for an in self.notes:
            an.identification = module.make_unique("n")

        


    def __str__(self):
        s = ""
        for tr in self.transitions:#sorted(self.transitions, key=lambda x: len(str(x)), reverse=True):
            s += str(tr) + "\n"
        for pl in self.places:#sorted(self.places, key=lambda x: len(str(x)), reverse=True):
            s += str(pl) + "\n"
        for an in self.notes:#sorted(self.notes, key=lambda x: len(str(x)), reverse=True):
            s += str(an) + "\n"
        s += self.header
        return s
        

    def show(self):
        s = "------------ Model ---------------\n"
        s += "Transitions: \n"
        for tr in self.transitions:
            s += str(tr) + "\n"
        s += "\nPlaces: \n"
        for pl in self.places:
            s += str(pl) + " <> " + pl.description.name + "\n"
        s += "\nNotes: \n"
        for c in self.notes:
            s += str(c) + "\n"
        s += "----------------------------------"
        print(s)

    
    def merge(self, distant):

        print("[MERGE] Starting merge process...")

        # ------ MERGING PLACES -------
        print("[MERGE] Merging PLACES")
        diffs = module.merge_nodes(self.places, distant.places)
        for diff in diffs:
            # Add node from different tree to this one
            self.add_place(diff)
        print(self.places)

        # ---- MERGING TRANSITIONS -----
        print("[MERGE] Merging TRANSITIONS")
        diffs = module.merge_nodes(self.transitions, distant.transitions)
        for diff in diffs:
            # Add node from different tree to this one
            self.add_tr(diff)
        print(self.places)

        # ----- MERGING NOTES ------
        print("[MERGE] Adding optionnal notes")
        # TO DO notes merging, but we need the be able to compare whole sentences
        _, nt_diffs = module.match(self.notes, distant.notes)
        # The notes that differ are added (the other are kept common for coherence by their associated places or transitions)
        for diff in nt_diffs:
            self.notes.append(diff)

        return "SUCCESS"


    def add_place(self, pl):
        self.places.append(pl)
        self.add_node(pl, 'end')

    def add_tr(self, tr):
        self.transitions.append(tr)
        self.add_node(tr, 0)

    def add_node(self, element, index):
        print("Adding ", element)
        if element.model == self:
            self.tree.move(element.node, self.node, index)
        else:
            print("Arbre différent")
            element.nodeify(self.tree, self.node, index)

"""
TODO:

ATTENTION si on rename pendant un merge, puisqu'on se base sur les noms de 1 modèle on risque d'avoir un conflit avec un autre nom spécifique au modèle distant
-> peut être renommer tout
-> renommer toutes les notes (il faut un "n" + un numéro )
-> gérer les retours à la ligne "\\n" dans les labels

    Compléter le ruleset proposé, tester et en décrire les limites.
    
    possibilité d'améliorations: 

        pour l'instant les attributs sont réécrits, comment rendre ca plus compréhensbile pour les utilisateurs? 
            ~~~peut être que lors du merge ils n'y toucheront plus beaucoup donc pas besoin
            sinon plusieurs possibilités:
                dictionnaire résumant les équivalences / matching qui ont été faits (bien aussi pour les logs / la prise de décision sur le merge)
                ne pas réécrire et grâce au dictionnaire on peut faire la comparaison et les prochaines aussi: les équivalences seront connues ?...
"""

"""
pb par ex:
The semantic similarity between 'car' and 'bus' is:
0.96
The semantic similarity between 'car' and 'vehicle' is:
0.8888888888888888
The semantic similarity between 'car' and 'automobile' is:
1.0

selon le cadre dans lequel on évolue il faut en fait gérer le threshold très précisément
si on a des bus et des automobiles qui sont censés être différents parceque on travaille 
dans le monde automobile c'est embêtant, mais comment savoir si on doit pouvoir les ditinguer ou pas?
et si on doit pouvoir distinguer les mots qui englobe la notion d'un autre



Peut être TRES intéressant de laisser le merge git se faire après coup pour garder le versionnage, labelisation etc...
--> CHANGER retroactivement l'historique des commits d'un utilisateur ?
--> cela permet de réécrire les fichiers sans write direct
(ne semble pas faisable)
Lors du merge ajouter artificiellement des lignes au début et à la fin pour éviter des problèmes de merge github ?
-> transmettre problème de merge à git (remonter exception) ?
-> ou traiter problème en local avec un visuel ?
-> Si il y a ontologie on peut proposer les changements et la personne valide rapidement ou non



Meme nom -> meme transition donc ajouter les éléments / comparer à la 
version commune pour voir ce qui a été enlevé pour supprimer
"""
    


