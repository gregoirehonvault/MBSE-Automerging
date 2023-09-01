import module

MARKER = "an"
DEFAULT_EMB = []

def is_note(line):
    parts = line.split(" ")
    return parts[0] == MARKER


# Find the place with the given name in a list of places
def find_an(name, notes):
    for an in notes:
        if an.get_name() == name:
            return an
    return None

# Initialise place with artificial line
def no_line_an(id_nb, name):
    return Note(MARKER + " " + "n"+str(id_nb) + " " + "1 " + "{"+name+"}")

# In case no notes were defined to describe the place element
def extract_an(name, notes):
    an = find_an(name, notes)
    # Undefined notes are added to the place's description and the Model notes
    if an == None:
        # TO DO Be sure the next id number is the next integer (do not allow self defining)
        an = no_line_an(len(notes), name)
        notes.append(an)
    return an


class Note:
    identification = ""
    visible = 1 # 0 or 1 only
    name = "" # Corresponds to the name of the associated place, in the label
    label = ""
    embeddings = DEFAULT_EMB

    def __init__(self, line):
        if not is_note(line):
                raise TypeError("Parsing Error: Not a place")
        # Useful processing
        parts = line.split(" ")
        self.id = parts[1]
        self.visible = parts[2]
        # Parse label without the surrounding brackets
        k = 3
        while k < len(parts):
            self.label += parts[k] + " "
            k += 1
        # Removing brackets and final space
        self.label = self.label[1:-2]
        # Separating name and description in the label (separated by "-")
        try:
            idx = self.label.index("-")
            self.name = self.label[:idx-1]
            self.label = self.label[idx+2:]
            print(f"Found note associated with {self.name}")
        except ValueError:
            print("Found lone note")


    def __str__(self):
        return " ".join([MARKER, self.identification, str(self.visible), "{"+self.name + bool(self.name)*" - " + self.label +"}"])
    
    def is_embedded(self):
        return len(self.embeddings) != len(DEFAULT_EMB)
    
    def get_name(self):
        return self.name
    
    def get_label(self):
        return self.label

    def eq_rate(self, distant, match_name=False):
        return module.desc_similarity(self, distant, match_name)

    # Overwriting all distant attributes
    def merge(self, distant):
        distant.name = self.name
        distant.content = self.label


        
    