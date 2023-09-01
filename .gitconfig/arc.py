import place, module

MARKER = "ar"

# Arc kinds are directly defined by their symbols
NORMAL_ARC = "*"
TEST_ARC =  "?"
INHIBITOR_ARC = "?-"
STOPWATCH_ARC = "!"
STOPWATCH_INHIBITOR_ARC = "!-"
DEFAULT_WEIGHT = 1
SYMBOLS = [NORMAL_ARC, TEST_ARC, INHIBITOR_ARC, STOPWATCH_ARC, STOPWATCH_INHIBITOR_ARC]


class Arc:
    kind = NORMAL_ARC
    weight = DEFAULT_WEIGHT


    def __init__(self, string, model):
        
        self.model = model
        self.previous = None

        if string[-1].isdigit() and string[-2] in SYMBOLS: 
            self.kind = string[-2]
            self.weight = string[-1]
            self.previous = place.extract_pl(string[:-2], model)
        else:
            self.previous = place.extract_pl(string, model)
        
        # Only upon completion
        self.node = self.model.tree.insert('', 'end', text=str(self), open=True)

        
    def __str__(self):
        return (self.previous).name + (self.kind != NORMAL_ARC or self.weight != DEFAULT_WEIGHT) * (self.kind + str(self.weight))

    def __repr__(self):
        return str(self)

    def is_default_weight(self):
        return self.weight == DEFAULT_WEIGHT

    # On retourne le nom de la place associée
    def get_name(self):
        return self.previous.get_name()
    
    def get_weight(self):
        return self.weight
    
    def get_kind(self):
        return self.kind

    def set_kind(self, value):
        # Will raise Value errors if any issue
        kind = str(value)
        if len(kind) != 1:
            raise ValueError
        self.kind = kind
        self.update_view()

    def set_weight(self, value):
        # If empty string is passed, int() will raise a ValueError
        weight = int(value)
        if weight < 0:
            raise ValueError
        self.weight = weight
        self.update_view()

    def update_view(self):
        self.model.tree.item(self.node, text=str(self))
        self.previous.update_view()

    # Equivalence rate for arcs are directly those of corresponding places
    # TO DO limite = si 1 arc conceptualisait un "test" sur une action etc, et qu'il est remplacé par plusieurs pour faire la même action mais en + fin, on peut pas le savoir
    def eq_rate(self, distant, match_name):
        if self.kind != distant.kind:
            return 0
        else:
            return self.previous.eq_rate(distant.previous, match_name=True)
    
    def merge_kind(self, distant):
        if self.kind != distant.kind:
            raise module.KindClashError(self, distant)      

    def merge_weight(self, distant):
        if self.weight != distant.weight:
            if self.is_default_weight():
                self.set_weight(distant.weight)
            elif distant.is_default_weight():
                distant.set_weight(self.weight)
            else:
                raise module.WeightClashError(self, distant)
        else:
            distant.set_weight(self.weight)

    def diff(self, distant):
        return self.diff_kind(distant), self.diff_weight(distant)

    def merge(self, distant):
        # Merge associated place
        self.merge_weight(distant)
        self.merge_kind(distant)
        #self.previous.merge(distant.previous)
        # only equal elements (equal places) should be matched
        # so no need to merge them
        
