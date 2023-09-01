import module, note

MARKER = "pl"
LABEL_SEPARATION = ":"
DEFAULT_MARKING = 0


#Determine if a string line represents a place
def is_pl(line):
    parts = line.split(" ")
    return parts[0] == MARKER

# Find the place with the given name in a list of places
def find_pl(name, places):
    for pl in places:
        if pl.name == name:
            return pl
    return None

# Initialise place with artificial line
def no_line_pl(name, model):
    return Place(MARKER + " " + name, model)

# Extract place line out of existing written place lines in the file. 
# If such a place does not exist, we create it from scratch
def extract_pl(string, model):
    places = model.places
    notes = model.notes
    pl = find_pl(string, places)
    if pl == None:
        pl = no_line_pl(string, model)
        # Enables no_line places defined/instanciated in transition arcs 
        # to be added to the model's places
        model.add_place(pl)
    return pl


class Place:
    name = ""
    label = ""
    marking = DEFAULT_MARKING
    description = ""


    def __init__(self, line, model):

        self.model = model
        notes = model.notes


        if not is_pl(line):
            # TO DO créer une exception appropriée
            raise TypeError("Parsing Error: Not a place")
        # Useful processing
        pl = line.split(" ")

        for k in range(1, len(pl)):

            if pl[k-1] == MARKER:
                self.name = pl[k]

            elif pl[k-1] == LABEL_SEPARATION:
                self.label = pl[k]
            
            elif pl[k].startswith("("):
                self.marking = int(pl[k][1])

        self.description = note.extract_an(self.name, notes)
        # Only upon completion
        self.node = self.model.tree.insert('', 'end', text=str(self), open=True)


    def __str__(self):

        if self.is_default():
            return ""

        join_list = [MARKER, self.name]

        if not self.is_default_label():
            join_list += [LABEL_SEPARATION, self.label]

        if self.marking != DEFAULT_MARKING:
            marking_str = "(" + str(self.marking) + ")"
            join_list += [marking_str]

        return " ".join(join_list)
    

    def __repr__(self):
        return str(self)

    def is_default_label(self):
        return self.label == ""

    def is_default_marking(self):
        return self.marking == 0

    def is_default(self):
        return self.name == "" and self.label == "" and self.marking == 0 
    
    def get_name(self):
        return self.name
    
    def get_label(self):
        return self.label
    
    def get_marking(self):
        return self.marking
    
    def get_desc(self):
        return self.description
    
    def get_header(self):
        return self.name + " " + self.label
    
    def set_marking(self, value):
        marking = int(value)
        if marking < 0:
            raise ValueError()
        self.marking = marking
        self.update_view()

    def set_name(self, name):
        self.name = name
        self.update_view()

    def set_label(self, label):
        self.label = label
        self.update_view()

    def update_view(self):
        self.model.tree.item(self.node, text=str(self))

    def eq_rate(self, distant, match_name=False):
        return module.similarity(self, distant, match_name)

    def merge_marking(self, distant):
        if self.marking != distant.marking:
            if self.is_default_marking():
                self.marking = distant.marking
            elif distant.is_default_marking():
                distant.marking = self.marking
            else:
                raise module.MarkingClashError(self, distant)

    def merge(self, distant):

        # We have to put the merge that could create a ClashError first
        # Merging marking and associated note
        self.merge_marking(distant)
        # Name is kept by place receiving the merge
        # Merging is done taking into account equivalent labels so no need to update self label
        # If a new label was provided by the other instance, we add it
        if self.is_default_label():
            self.set_label(distant.label)
        # Overwriting distant attributes for coherence (later needed for eq_rate() methods)
        distant.set_label(self.label)
        # Unique id
        distant.set_name(self.name)
        
        # TO do description qui apparait sur le treeview
        self.description.merge(distant.description)
        
    def nodeify(self, tree, root, index):
        # TO DO temporary
        tree.insert(root, index, text=str(self) ,open=True)