import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import json
import os

DARK_BG = "#1e1e1e"
DARK_FRAME = "#2d2d2d"
DARK_CANVAS = "#252526"
ACCENT = "#007acc"

SAVE_FILE = "rpg_save.json"

players_data = {
    "ENZO": {"classe": "PALADINO"}, "HENRIQUE": {"classe": "ANÃO"},
    "KAUÃ": {"classe": "ELFO"}, "VITOR": {"classe": "BERSERKER"},
    "RUAN": {"classe": "LADINO"}, "VINICIUS": {"classe": "MAGO(Arcano)"},
    "MATHEUS": {"classe": "CLÉRIGO"}, "THIAGO": {"classe": "CURANDEIRO"},
    "RAFA": {"classe": "MAGO(Necromante)"},
}

DEFAULT_ATTRS = ["FR", "DE", "IN", "AG", "PR", "MG", "SOR"]

def create_player(name, classe):
    return {
        "nome": name, "classe": classe, "xp": 0, "nivel": 1,
        "status_extras": {
            "vida": {"atual": 10, "max": 10},
            "energia": {"atual": 10, "max": 10}
        },
        "atributos": {attr: 0 for attr in DEFAULT_ATTRS},
        "documentos": {},
        "notas": "",
        "notas_atributos": ""
    }

if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        players = json.load(f)
    for name, info in players.items():
        if "status_extras" not in info:
            info["status_extras"] = {
                "vida": {"atual": info.get("vida", 10), "max": info.get("vida_max", 10)},
                "energia": {"atual": info.get("energia", 10), "max": info.get("energia_max", 10)}
            }
        if "notas_atributos" not in info: info["notas_atributos"] = ""
        if "notas" not in info: info["notas"] = ""
        if "atributos" not in info: info["atributos"] = {attr: 0 for attr in DEFAULT_ATTRS}
        if "documentos" not in info: info["documentos"] = {}
else:
    players = {name: create_player(name, info["classe"]) for name, info in players_data.items()}

def save_game():
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(players, f, ensure_ascii=False, indent=4)

def add_new_status(player_name):
    nome = simpledialog.askstring("Novo Estado", "Nome do estado (ex: Mana, Escudo):")
    if nome:
        nome = nome.upper()
        players[player_name]["status_extras"][nome] = {"atual": 10, "max": 10}
        save_game(); update_list_frame(); update_players_frame()

def add_new_attribute(player_name):
    nome = simpledialog.askstring("Novo Atributo", "Nome do atributo (ex: CARISMA, SORTE):")
    if nome:
        nome = nome.upper()
        if nome in players[player_name]["atributos"]:
            messagebox.showinfo("Aviso", "Este atributo já existe!")
            return
        players[player_name]["atributos"][nome] = 0
        save_game(); update_list_frame(); update_players_frame()

def remove_attribute(player_name, attr_key):
    if attr_key in DEFAULT_ATTRS:
        messagebox.showwarning("Proibido", "Atributos padrão não podem ser removidos.")
        return
    if messagebox.askyesno("Confirmar", f"Excluir atributo '{attr_key}'?"):
        del players[player_name]["atributos"][attr_key]
        save_game(); update_list_frame(); update_players_frame()

def adjust_dynamic_stat(player_name, key, delta, is_max=False):
    status = players[player_name]["status_extras"][key]
    if is_max: status["max"] = max(0, status["max"] + delta)
    else: status["atual"] = max(0, status["atual"] + delta)
    if status["atual"] > status["max"]: status["atual"] = status["max"]
    save_game(); update_list_frame(); update_players_frame()

def remove_status(player_name, key):
    if key in ["vida", "energia"]: return
    if messagebox.askyesno("Confirmar", f"Excluir {key}?"):
        del players[player_name]["status_extras"][key]
        save_game(); update_list_frame(); update_players_frame()

def add_new_document(player_name):
    nome = simpledialog.askstring("Novo Documento", "Nome (História, Pets, NPCs...):")
    if nome:
        nome = nome.strip().upper()
        if nome in players[player_name]["documentos"]:
            messagebox.showinfo("Aviso", "Já existe um documento com este nome!")
            return
        players[player_name]["documentos"][nome] = ""
        save_game()
        update_list_frame()

def update_players_frame():
    for widget in players_frame.winfo_children(): widget.destroy()
    for idx, (name, data) in enumerate(players.items()):
        row, col = idx // 2, idx % 2
        f = tk.Frame(players_frame, bd=1, relief="solid", padx=5, pady=5, bg=DARK_CANVAS, width=240, height=110)
        f.grid(row=row, column=col, padx=5, pady=5, sticky="n")
        f.pack_propagate(False)
        
        tk.Label(f, text=f"{name} ({data['classe']})", font=("Arial", 9, "bold"), bg=DARK_CANVAS, fg="white").pack(anchor="w")
        
        txt_status = f"LVL: {data['nivel']} | XP: {data['xp']}\n"
        for k, v in data['status_extras'].items():
            txt_status += f"{k.upper()}: {v['atual']}/{v['max']}  "
        
        tk.Label(f, text=txt_status, bg=DARK_CANVAS, fg=ACCENT, font=("Arial", 8), justify="left", wraplength=220).pack(anchor="w")
        tk.Button(f, text="Gerenciar", bg=DARK_BG, fg="white", font=("Arial", 7), command=lambda n=name: select_player(n)).pack(side="bottom", fill="x")

def show_state():
    player = players[selected_player]
    f_up = tk.Frame(attributes_frame, bg=DARK_FRAME); f_up.pack(fill="x", pady=2)
    tk.Label(f_up, text=f"LVL: {player['nivel']}", bg=DARK_FRAME, fg="white").pack(side="left")
    tk.Button(f_up, text="+", width=2, command=lambda: [players[selected_player].update({"nivel": player['nivel']+1}), save_game(), update_list_frame(), update_players_frame()]).pack(side="left", padx=2)
    tk.Button(f_up, text="-", width=2, command=lambda: [players[selected_player].update({"nivel": max(1, player['nivel']-1)}), save_game(), update_list_frame(), update_players_frame()]).pack(side="left")
    
    tk.Label(f_up, text=" | XP:", bg=DARK_FRAME, fg="white").pack(side="left", padx=5)
    e_xp = tk.Entry(f_up, width=4); e_xp.insert(0, "0"); e_xp.pack(side="left")
    tk.Button(f_up, text="+", width=2, command=lambda: [players[selected_player].update({"xp": player['xp']+int(e_xp.get() or 0)}), save_game(), update_list_frame(), update_players_frame()]).pack(side="left", padx=2)

    tk.Button(attributes_frame, text="+ ESTADO", bg="#28a745", fg="white", font=("Arial", 8, "bold"), command=lambda: add_new_status(selected_player)).pack(fill="x", pady=5)

    for key, v in player["status_extras"].items():
        f = tk.Frame(attributes_frame, bg=DARK_FRAME); f.pack(fill="x", pady=1)
        if key not in ["vida", "energia"]:
            tk.Button(f, text="x", bg="#444", fg="red", bd=0, command=lambda k=key: remove_status(selected_player, k)).pack(side="left")
        
        tk.Label(f, text=f"{key.upper()}: {v['atual']}/{v['max']}", bg=DARK_FRAME, fg="white", width=12, anchor="w").pack(side="left")
        tk.Button(f, text="+", width=2, command=lambda k=key: adjust_dynamic_stat(selected_player, k, 1)).pack(side="left")
        tk.Button(f, text="-", width=2, command=lambda k=key: adjust_dynamic_stat(selected_player, k, -1)).pack(side="left")
        tk.Label(f, text="M:", bg=DARK_FRAME, fg="grey").pack(side="left", padx=2)
        tk.Button(f, text="+", width=2, command=lambda k=key: adjust_dynamic_stat(selected_player, k, 1, True)).pack(side="left")
        tk.Button(f, text="-", width=2, command=lambda k=key: adjust_dynamic_stat(selected_player, k, -1, True)).pack(side="left")

    tk.Label(attributes_frame, text="Notas de Estado:", bg=DARK_FRAME, fg="white").pack(anchor="w", pady=(10,0))
    t_notas = tk.Text(attributes_frame, height=6, bg=DARK_CANVAS, fg="white", font=("Arial", 9))
    t_notas.pack(fill="both", expand=True, pady=5)
    t_notas.insert("1.0", player["notas"])
    t_notas.bind("<KeyRelease>", lambda e: [players[selected_player].update({"notas": t_notas.get("1.0", "end-1c")}), save_game()])

def show_attributes():
    player = players[selected_player]
    
    tk.Button(attributes_frame, text="+ ATRIBUTO", bg="#007acc", fg="white", font=("Arial", 8, "bold"), command=lambda: add_new_attribute(selected_player)).pack(fill="x", pady=5)

    for attr, val in player["atributos"].items():
        f = tk.Frame(attributes_frame, bg=DARK_FRAME); f.pack(fill="x")
        
        if attr not in DEFAULT_ATTRS:
            tk.Button(f, text="x", bg="#444", fg="red", bd=0, command=lambda a=attr: remove_attribute(selected_player, a)).pack(side="left", padx=(0,5))
            
        tk.Label(f, text=f"{attr}: {val}", width=10, bg=DARK_CANVAS, fg="white").pack(side="left", pady=1)
        tk.Button(f, text="+", width=2, command=lambda a=attr: [player["atributos"].update({a: player["atributos"][a]+1}), save_game(), update_list_frame()]).pack(side="left", padx=2)
        tk.Button(f, text="-", width=2, command=lambda a=attr: [player["atributos"].update({a: max(0, player["atributos"][a]-1)}), save_game(), update_list_frame()]).pack(side="left")

    tk.Label(attributes_frame, text="Notas de Atributos:", bg=DARK_FRAME, fg="white").pack(anchor="w", pady=(10,0))
    t_attr_notas = tk.Text(attributes_frame, height=8, bg=DARK_CANVAS, fg="white", font=("Arial", 9))
    t_attr_notas.pack(fill="both", expand=True, pady=5)
    t_attr_notas.insert("1.0", player.get("notas_atributos", ""))
    t_attr_notas.bind("<KeyRelease>", lambda e: [players[selected_player].update({"notas_atributos": t_attr_notas.get("1.0", "end-1c")}), save_game()])

def show_documentation():
    player = players[selected_player]
    global open_doc_name

    if 'open_doc_name' in globals() and open_doc_name:
        header_doc = tk.Frame(attributes_frame, bg=DARK_FRAME); header_doc.pack(fill="x", pady=5)
        tk.Button(header_doc, text="← VOLTAR", font=("Arial", 7, "bold"), bg="#555", fg="white", 
                  command=lambda: [globals().update({'open_doc_name': None}), update_list_frame()]).pack(side="left")
        tk.Label(header_doc, text=open_doc_name, bg=DARK_FRAME, fg=ACCENT, font=("Arial", 10, "bold")).pack(side="left", padx=10)
        
        txt_doc = tk.Text(attributes_frame, bg=DARK_CANVAS, fg="white", font=("Arial", 10), insertbackground="white", wrap="word")
        txt_doc.pack(fill="both", expand=True, pady=5)
        txt_doc.insert("1.0", player["documentos"][open_doc_name])
        
        txt_doc.bind("<KeyRelease>", lambda e: [player["documentos"].update({open_doc_name: txt_doc.get("1.0", "end-1c")}), save_game()])
    
    else:
        tk.Label(attributes_frame, text="DOCUMENTAÇÃO DO MESTRE", font=("Arial", 10, "bold"), bg=DARK_FRAME, fg="white").pack(pady=5)
        info_txt = "Espaço para anotações de Histórias, NPCs, Pets e observações gerais."
        tk.Label(attributes_frame, text=info_txt, font=("Arial", 8, "italic"), bg=DARK_FRAME, fg="#aaa", wraplength=350).pack(pady=5)
        
        tk.Button(attributes_frame, text="+ NOVO DOCUMENTO", bg="#28a745", fg="white", font=("Arial", 8, "bold"), 
                  command=lambda: add_new_document(selected_player)).pack(fill="x", pady=10)
        
        for doc_key in player["documentos"].keys():
            btn = tk.Button(attributes_frame, text=doc_key, bg=DARK_CANVAS, fg="white", font=("Arial", 9), anchor="w", padx=10,
                            command=lambda d=doc_key: [globals().update({'open_doc_name': d}), update_list_frame()])
            btn.pack(fill="x", pady=2)

def select_player(name):
    global selected_player, open_doc_name
    selected_player = name
    open_doc_name = None
    attributes_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
    update_list_frame()

def update_list_frame():
    for widget in attributes_frame.winfo_children(): widget.destroy()
    if not selected_player: return
    
    header = tk.Frame(attributes_frame, bg=DARK_FRAME); header.pack(fill="x")
    tk.Label(header, text=selected_player, font=("Arial", 11, "bold"), bg=DARK_FRAME, fg="white").pack(side="left")
    tk.Button(header, text="X", bg="#aa3333", fg="white", font=("Arial", 8), command=lambda: attributes_frame.grid_remove()).pack(side="right")
    
    tab_f = tk.Frame(attributes_frame, bg=DARK_FRAME); tab_f.pack(fill="x", pady=5)
    
    tk.Button(tab_f, text="Estado", font=("Arial", 8), command=lambda: [current_tab.set("estado"), update_list_frame()]).pack(side="left", padx=2)
    tk.Button(tab_f, text="Atributos", font=("Arial", 8), command=lambda: [current_tab.set("atributos"), update_list_frame()]).pack(side="left", padx=2)
    tk.Button(tab_f, text="Documentação", font=("Arial", 8), command=lambda: [current_tab.set("documentacao"), update_list_frame()]).pack(side="left", padx=2)
    
    if current_tab.get() == "estado": show_state()
    elif current_tab.get() == "atributos": show_attributes()
    elif current_tab.get() == "documentacao": show_documentation()

root = tk.Tk()
root.title("Mestre RPG")
root.geometry("1000x700")
root.configure(bg=DARK_BG)
selected_player = None
open_doc_name = None
current_tab = tk.StringVar(value="estado")
root.grid_columnconfigure(0, weight=1); root.grid_columnconfigure(1, weight=1); root.grid_rowconfigure(0, weight=1)

container = tk.Frame(root, bg=DARK_CANVAS)
container.grid(row=0, column=0, sticky="nsew")
canvas = tk.Canvas(container, bg=DARK_CANVAS, highlightthickness=0)
scroll = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
players_frame = tk.Frame(canvas, bg=DARK_CANVAS)
canvas.create_window((0,0), window=players_frame, anchor="nw")
canvas.configure(yscrollcommand=scroll.set)
canvas.pack(side="left", fill="both", expand=True); scroll.pack(side="right", fill="y")
players_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

attributes_frame = tk.Frame(root, bg=DARK_FRAME, bd=2, relief="sunken", padx=10)

update_players_frame()
root.mainloop()
