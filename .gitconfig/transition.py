import module, arc, note

MARKER = "tr"
LABEL_SEPARATION = ":"
DEFAULT_T0 = "0"
DEFAULT_T1 = "w"
PL_SEPARATION = "->"
BRACKETS = ["[", "]"]


# Determine is a string line represents a transition
def is_tran(line):
    parts = line.split(" ")
    return parts[0] == MARKER


class Transition:
    """
    --- Instance variables ---
    name
    label
    label_embedding
    bracket_open
    t0
    t1
    bracket_close
    start_arc
    finish_arc
    description
    """
    # Initialisation through parsing
    # We start with all the places of the model 
    # that were parsed during model init
    def __init__(self, line, model):

        notes = model.notes
        self.model = model

        if not is_tran(line):
            print("Parsing Error: Not a transition")
            return self
        
        # Useful processing
        tr = line.split(" ")
        start = True

        self.name = ""
        self.start_arc = []
        self.finish_arc = []
        self.label = ""
        self.label_embedding = ""
        self.t0 = DEFAULT_T0
        self.t1 = DEFAULT_T1
        self.bracket_open = "["
        self.bracket_close = "]"

        self.node = None
        self.start_node = None
        self.finish_node = None

        # Treeview, name defined after parse completion
        self.node = self.model.tree.insert('', 'end', text="", open=True)
        self.start_node = self.model.tree.insert(self.node, 'end', text="IN ARCS")
        self.finish_node = self.model.tree.insert(self.node, 'end', text="OUT ARCS")


        # Iteration on all starting and finishing places
        k = 0
        while k < len(tr):

            if tr[k] == MARKER:
                self.name = tr[k+1]
                k += 1 # to skip next parsed element

            elif tr[k] == LABEL_SEPARATION:
                k+=1
                # Multiplue words label
                if tr[k].startswith("{"):
                    while not tr[k].endswith("}"):
                        self.label += tr[k] + " "
                        k+=1
                    # Add last element of the list
                    self.label += tr[k]
                    # remove brackets
                    self.label = self.label[1:-1] 
                # One word label (no brackets)
                else:
                    self.label = tr[k]
            
            elif tr[k].startswith("[") or tr[k].startswith("]"):
                self.set_time(tr[k])
                

            # Next places will be in the finish places
            elif tr[k] == PL_SEPARATION:
                start = False

            # TO DO better marker?
            elif tr[k] is not None and tr[k] != '':

                connection = arc.Arc(tr[k], self.model)
                if start:
                    self.add_start(connection)
                else:
                    self.add_finish(connection)
            k+=1
        
        self.description = note.extract_an(self.name, notes)
        # Overwrite name after being defined
        self.model.tree.item(self.node, text=self.get_header())


    def __str__(self):

        join_list = [MARKER, self.name]

        # Optional label separation and label
        if not self.is_default_label():
            join_list += [LABEL_SEPARATION, "{"+self.label+"}"]

        join_list += [self.get_time()]

        # Starting arcs then separation then finishing arcs
        for ar in self.start_arc:
            join_list += [str(ar)]

        join_list += [PL_SEPARATION]

        for ar in self.finish_arc:
            join_list += [str(ar)]

        return " ".join(join_list)
        
    def is_default_label(self):
        return self.label == ""

    def is_default_t1(self):
        return self.t1 == DEFAULT_T1

    def is_default_t0(self):
        return self.t0 == 0
    
    def get_name(self):
        return self.name
    
    def get_label(self):
        return self.label
    
    def get_time(self):
        return self.bracket_open + self.t0 + "," + self.t1 + self.bracket_close
    
    def get_desc(self):
        return self.description
    
    def get_header(self):
        return self.name + " " + self.label
    
    def set_name(self, name):
        self.name = name
        self.update_view()

    def set_label(self, label):
        self.label = label
        self.update_view()
    
    def update_view(self):
        self.model.tree.item(self.node, text=self.get_header())
        for ar in (self.start_arc + self.finish_arc):
            ar.update_view() # TODO mauvais

    def set_time(self, value):
        time = str(value)
        if len(time) < 5:
            raise ValueError
        sep = time.index(",")
        
        bracket_open = time[0]
        t0 = time[1:sep]
        t1 = time[sep+1:-1]
        bracket_close = time[-1]

        temporal_issue = False
        try:
            temporal_issue = int(t0) > int(t1)
        except ValueError:
            # If characters are used instead of integers
            pass
        if temporal_issue:
            raise ValueError
        if (bracket_open not in BRACKETS or
            bracket_close not in BRACKETS):
            raise ValueError
        
        # Write values
        self.bracket_open = bracket_open
        self.t0 = t0
        self.t1 = t1
        self.bracket_close = bracket_close
        # TO DO necessary?
        self.update_view()

    # Returns value for merged time. Any changes to both times will return an error ? TO DO raise it and handle exceptions in eq_rate? handle brackets
    def merge_time(self, distant):
        if (self.bracket_open != distant.bracket_open or 
            self.bracket_close != distant.bracket_close):
            raise module.TimeClashError(self, distant)
        if self.t0 != distant.t0:
            if self.is_default_t0():
                self.t0 = distant.t0
            elif distant.is_default_t0():
                distant.t0 = self.t0
            else:
                raise module.TimeClashError(self, distant)
        if self.t1 != distant.t1:
            if self.is_default_t1():
                self.t1 = distant.t1
            elif distant.is_default_t1():
                distant.t1 = self.t1
            else:
                raise module.TimeClashError(self, distant)
    
    # Defines if 2 transitions have the same "base" onto which elements were added
    # TO DO how to find if elements were removed?? (have a third version of the file?)
    def eq_rate(self, distant, match_name=False):
        print(f"Equivalence rate for transitions: {self.name} | {distant.name}")
        return module.similarity(self, distant, match_name)
    
        # If no matching name was found, checking if given transitions have common starts and finishes
        # to get the ratio of common elements
        n = len(self.start_arc + distant.start_arc + self.finish_arc + distant.finish_arc)
        print("Start arcs:")
        n_start = len(module.match(self.start_arc, distant.start_arc)[0])
        print("Finish arcs:")
        n_finish = len(module.match(self.finish_arc, distant.finish_arc)[0])

        # TO DO ici le biais est certainement en faveur des éléments
        # qui ont des start ET finish places et en défaveur de ce qui en ont pas
        # en start ou finish, décider d'une rate prenant en compte la structure ET le nom
        # on pourrait dire "ok veto sur le nom, mais rate sur la structure uniquement"
        if n_start > 0 and n_finish > 0:
            print(">> Common arcs found")
            return (n_start + n_finish)/n 
        else:
            print(">> Not enough structural matching found\n")
            return 0


    def merge(self, distant):

        print(f"MERGING transitions {self.name} with {distant.name}")

        # Anything that could cause exceptions first
        self.merge_time(distant)

        if self.is_default_label():
            self.set_label(distant.label)

        # Overwriting distant attributes for coherence
        distant.set_label(self.label)
        distant.set_name(self.name)

        # ----- NOW HANDLING ARCS ------
        # We renamed the matched places to keep exact same names
        # so the matched items returned by the solver should be matched with the same items
        module.merge_nodes(self.start_arc, distant.start_arc)
        module.merge_nodes(self.finish_arc, distant.finish_arc)
        distant.start_arc = self.start_arc
        distant.finish_arc = self.finish_arc

    def add_start(self, ar):
        self.start_arc.append(ar)
        self.model.tree.move(ar.node, self.start_node, 'end')

    def add_finish(self, ar):
        self.finish_arc.append(ar)
        self.model.tree.move(ar.node, self.finish_node, 'end')


    def nodeify(self, tree, root, index):
        # TO DO temporary
        
        tree.insert(root, index, text=self.get_header() ,open=True)