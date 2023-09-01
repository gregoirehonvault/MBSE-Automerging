import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import model
import argparse
import sys


class Menuview():

    def __init__(self, file1=None, file2=None):
        # Create the Tkinter window
        self.window = tk.Tk()
        self.window.title("Tina merger")

        self.file1, self.file2 = file1, file2
        self.m1, self.m2 = None, None

        # ---- ROW 0 ----
        # Control buttons
        tk.Button(self.window, text="Start merge", command=self.merge).grid(row=0, column=0, columnspan=2)
        
        # ---- ROW 1 ----
        # Indication messages
        tk.Label(self.window, text="Model 1", font=('Helvetica', 14)).grid(row = 1, column = 0)
        tk.Label(self.window, text="Model 2", font=('Helvetica', 14)).grid(row = 1, column = 1)

        # ---- ROW 2 ----
        # Create the Treeview widgets
        tree1 = ttk.Treeview(self.window, padding=0)
        tree1.grid(row=2, column=0, padx=5, pady=20)
        tree2 = ttk.Treeview(self.window, padding=0)
        tree2.grid(row=2, column=1, padx=5, pady=20)
        self.tree1, self.tree2 = tree1, tree2

        # ---- ROW 3 ----
        # Important for further functions
        self.show_clashframe()

        # ---- ROW 4 ----
        self.prompt = tk.StringVar()
        tk.Label(self.window, textvariable=self.prompt).grid(row=4, column=0)
        tk.Button(self.window, text="Close", command=self.window.destroy).grid(row=4, column=1)

        # Loading to see files trees before starting
        if file1 and file2:
            self.file1, self.file2 = file1, file2
            self.init_models()


    def init_models(self):
        if not (self.file1 and self.file2):
            self.browseFiles()
        # TO DO handle Errors from no file
        self.m1 = model.Model(self.file1, self.tree1, self.clash_frame)
        self.m2 = model.Model(self.file2, self.tree2, self.clash_frame)

    # Function for opening the
    # file explorer window
    def browseFiles(self):
        self.file1 = filedialog.askopenfilename(initialdir = "./",
                                            title = "Select file for model 1",
                                            filetypes = (("tina files",
                                                            "*.net*"),
                                                        ("all files",
                                                            "*.*")))
        
        self.file2 = filedialog.askopenfilename(initialdir = "./",
                                            title = "Select file for model 1",
                                            filetypes = (("tina files",
                                                            "*.net*"),
                                                        ("all files",
                                                            "*.*")))


    def merge(self):
        # If not none they are defined
        if self.m1 and self.m2:
            finished = self.m1.merge(self.m2)
            if finished:
                self.prompt.set("Merge Done")
                f = open(self.file1, "w")
                f.write(str(self.m1))
                f.close()
                f = open(self.file2, "w")
                f.write(str(self.m1))
                f.close()
        else:
            self.init_models()
        

    def reset_clash_tab(self):
        self.hide_clashframe()
        self.show_clashframe()
        
    def hide_clashframe(self):
        if self.clash_frame != None:
            self.clash_frame.destroy()
            self.clash_frame = None

    def show_clashframe(self):
        self.clash_frame = tk.Frame(self.window)
        self.clash_frame.grid(row=3, column=0, columnspan=2)


    """
    def highlight_clash():
        tree1.tag_configure('test', background='orange', foreground='red')
        tree2.item(node1, open=True)
    # UPDATE la view pour que les changements apparaissent --> setters et getters / highlight les clashs
    fichiers de dictionnaires ? Ontologies?
    
    # METTRE DE VRAIS DESCRIPTIONS POUR LES PLACES / DE VRAIS LABELS / DE VRAIS NOMS DE TRANSITIONS pas nom_tr1, taratata...
                puis push avec tout ca (avec les model)
                ajouter la phrase qui n'a aucun rapport ? en transition supplémentaire ? ou place + simple
            refaire tous les tests avec ces modifs pour voir que la démo fonctionne 
                PUIS PUSH SUR GIT ! AVEC ! les fichiers texte buffer.net, buffer1.net, merged.net....

    ajouter la descriptino correspondante quand un élément est ajouté....
    (ou alors pour write le fichier model il faut parcourir les éléments dans ce cas...)
    """


class Clashview():

    def __init__(self, clash, clash_frame):

        self.clash = clash

        self.frame = tk.Frame(clash_frame)
        self.frame.pack()

        self.user_input = tk.StringVar()

        # Prompt
        self.prompt = tk.StringVar()
        tk.Label(self.frame, textvariable=self.prompt, font=('Helvetica', 14)).pack()

        # Input
        self.text_input = tk.Text(self.frame, width=10, height=1)
        self.text_input.pack()

        # Solve conflict
        self.validate = tk.Button(self.frame, text="Validate", command=self.fetch_value)
        self.validate.pack()


    def fetch_value(self):
        self.user_input.set(self.text_input.get("1.0", "end-1c"))
        #Comment delete?

    def try_merge(self):
        finished = self.clash.try_merge
        if finished:
            self.frame.destroy()

    def print(self, m):
        self.prompt.set(m)

    def destroy(self):
        self.frame.destroy()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='Tina merger',
                    description='"Smart" tina merging helper')
    parser.add_argument('--file1')
    parser.add_argument('--file2')
    args = parser.parse_args()
    view = Menuview(args.file1, args.file2)
    view.window.mainloop()
    # Successful merge
    sys.exit(0)
    


