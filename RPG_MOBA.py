import flet as ft
import json
import os

SAVE_FILE = "rpg_save.json"
DEFAULT_ATTRS = ["FR", "DE", "IN", "AG", "PR", "MG", "SOR"]
DEFAULT_STATS = ["VIDA", "ENERGIA"]

players_data_initial = {
    "ENZO": {"classe": "PALADINO"}, "HENRIQUE": {"classe": "ANÃO"},
    "KAUÃ": {"classe": "ELFO"}, "VITOR": {"classe": "BERSERKER"},
    "RUAN": {"classe": "LADINO"}, "VINICIUS": {"classe": "MAGO(Arcano)"},
    "MATHEUS": {"classe": "CLÉRIGO"}, "THIAGO": {"classe": "CURANDEIRO"},
    "RAFA": {"classe": "MAGO(Necromante)"},
}

def create_player(name, classe):
    return {
        "nome": name, "classe": classe, "xp": 0, "nivel": 1,
        "status_extras": {
            "VIDA": {"atual": 10, "max": 10},
            "ENERGIA": {"atual": 10, "max": 10}
        },
        "atributos": {attr: 0 for attr in DEFAULT_ATTRS},
        "documentos": {}, 
        "notas": "",
        "notas_atributos": ""
    }

def load_game():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for name, info in data.items():
                if "status_extras" not in info: info["status_extras"] = {"VIDA": {"atual": 10, "max": 10}, "ENERGIA": {"atual": 10, "max": 10}}
                if "documentos" not in info: info["documentos"] = {}
                if "notas" not in info: info["notas"] = ""
                if "notas_atributos" not in info: info["notas_atributos"] = ""
                if "nivel" not in info: info["nivel"] = 1
                if "xp" not in info: info["xp"] = 0
            return data
    return {name: create_player(name, info["classe"]) for name, info in players_data_initial.items()}

players = load_game()

def save_game():
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(players, f, ensure_ascii=False, indent=4)

def main(page: ft.Page):
    page.title = "JOGADORES VALDREN"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 10
    
    current_tab = "ESTADO"

    main_layout = ft.Column(expand=True)
    page.add(main_layout)

    def route_main(_=None):
        render_home()

    def adjust_stat(p_name, stat_key, delta, is_max=False):
        stat = players[p_name]["status_extras"][stat_key]
        if is_max:
            stat["max"] = max(0, stat["max"] + delta)
            if stat["atual"] > stat["max"]:
                stat["atual"] = stat["max"]
        else:
            stat["atual"] = max(0, min(stat["max"], stat["atual"] + delta))
        save_game()
        render_details(p_name)

    def delete_item(p_name, category, key):
        if key in players[p_name][category]:
            del players[p_name][category][key]
            save_game()
            render_details(p_name)

    def add_custom_field(p_name, target_dict_key):
        def confirm_add(e):
            val = txt_new.value.strip().upper()
            if val:
                if target_dict_key == "status_extras":
                    players[p_name][target_dict_key][val] = {"atual": 10, "max": 10}
                elif target_dict_key == "atributos":
                    players[p_name][target_dict_key][val] = 0
                else:
                    players[p_name][target_dict_key][val] = ""
                save_game()
                dialog.open = False
                page.update()
                render_details(p_name)

        txt_new = ft.TextField(label="Nome do Campo", autofocus=True)
        dialog = ft.AlertDialog(
            title=ft.Text("Adicionar Novo"),
            content=txt_new,
            actions=[ft.TextButton("Adicionar", on_click=confirm_add)]
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def render_home():
        main_layout.controls.clear()
        page.appbar = ft.AppBar(title=ft.Text("LISTA DE JOGADORES"), center_title=True, bgcolor="#111111")
        
        grid = ft.ResponsiveRow()
        for name, data in players.items():
            grid.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(name, weight="bold", size=18),
                        ft.Text(data["classe"], color=ft.Colors.BLUE_200),
                        ft.Text(f"LVL: {data.get('nivel', 1)} | XP: {data.get('xp', 0)}", size=12),
                        ft.FilledButton("GERENCIAR", on_click=lambda e, n=name: render_details(n))
                    ], spacing=5),
                    padding=15, bgcolor="#2d2d2d", border_radius=10, col={"sm": 12, "md": 6, "lg": 4}
                )
            )
        main_layout.controls.append(ft.Column([grid], scroll=ft.ScrollMode.AUTO, expand=True))
        page.update()

    def render_details(name):
        nonlocal current_tab
        main_layout.controls.clear()
        p = players[name]

        page.appbar = ft.AppBar(
            leading=ft.TextButton("VOLTAR", on_click=route_main),
            title=ft.Text(f"{name}"),
            bgcolor="#1e1e1e",
            actions=[
                ft.TextButton("ESTADO", on_click=lambda _: set_tab("ESTADO", name)),
                ft.TextButton("ATRIB", on_click=lambda _: set_tab("ATRIBUTOS", name)),
                ft.TextButton("DOCS", on_click=lambda _: set_tab("DOCS", name)),
            ]
        )

        content = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=15)

        if current_tab == "ESTADO":
            content.controls.append(ft.Row([
                ft.Text("NÍVEL:", weight="bold"),
                ft.IconButton(ft.Icons.REMOVE_CIRCLE, on_click=lambda _: [p.update({"nivel": max(1, p.get("nivel", 1)-1)}), save_game(), render_details(name)]),
                ft.Text(str(p.get("nivel", 1)), size=22, weight="bold", color="blue"),
                ft.IconButton(ft.Icons.ADD_CIRCLE, on_click=lambda _: [p.update({"nivel": p.get("nivel", 1)+1}), save_game(), render_details(name)]),
            ], alignment=ft.MainAxisAlignment.START))

            xp_field = ft.TextField(width=70, value="0", text_align=ft.TextAlign.CENTER, dense=True)
            content.controls.append(ft.Row([
                ft.Text(f"XP: {p.get('xp', 0)}", weight="bold"),
                xp_field,
                ft.IconButton(ft.Icons.REMOVE, icon_color="red", on_click=lambda _: [
                    p.update({"xp": max(0, p.get('xp', 0) - (int(xp_field.value) if xp_field.value.isdigit() else 0))}),
                    save_game(), render_details(name)
                ]),
                ft.IconButton(ft.Icons.ADD, icon_color="green", on_click=lambda _: [
                    p.update({"xp": p.get('xp', 0) + (int(xp_field.value) if xp_field.value.isdigit() else 0)}),
                    save_game(), render_details(name)
                ])
            ]))
            
            content.controls.append(ft.Divider())
            content.controls.append(ft.FilledButton(" + NOVO STATUS", on_click=lambda _: add_custom_field(name, "status_extras")))

            for s_key, s_val in p["status_extras"].items():
                content.controls.append(
                    ft.Container(
                        bgcolor="#333333", padding=5, border_radius=8,
                        content=ft.Row(
                            wrap=True,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.IconButton(ft.Icons.DELETE, icon_color="red", visible=s_key not in DEFAULT_STATS, 
                                              on_click=lambda e, k=s_key: delete_item(name, "status_extras", k)),
                                ft.Text(f"{s_key}:", width=90, weight="bold"),
                                ft.Text(f"{s_val['atual']}/{s_val['max']}", width=70),
                                ft.IconButton(ft.Icons.REMOVE, on_click=lambda e, k=s_key: adjust_stat(name, k, -1)),
                                ft.IconButton(ft.Icons.ADD, on_click=lambda e, k=s_key: adjust_stat(name, k, 1)),
                                ft.VerticalDivider(),
                                ft.Text("M:"),
                                ft.IconButton(ft.Icons.ARROW_DROP_DOWN_CIRCLE_OUTLINED, on_click=lambda e, k=s_key: adjust_stat(name, k, -1, True)),
                                ft.IconButton(ft.Icons.ARROW_UPWARD_ROUNDED, on_click=lambda e, k=s_key: adjust_stat(name, k, 1, True)),
                            ]
                        )
                    )
                )
            
            content.controls.append(ft.TextField(label="Notas", value=p["notas"], multiline=True, on_change=lambda e: [p.update({"notas": e.control.value}), save_game()]))

        elif current_tab == "ATRIBUTOS":
            content.controls.append(ft.FilledButton(" + NOVO ATRIBUTO", on_click=lambda _: add_custom_field(name, "atributos")))
            for attr, val in p["atributos"].items():
                content.controls.append(
                    ft.Row(wrap=True, controls=[
                        ft.IconButton(ft.Icons.DELETE, icon_color="red", visible=attr not in DEFAULT_ATTRS, on_click=lambda e, a=attr: delete_item(name, "atributos", a)),
                        ft.Text(attr, width=80, weight="bold"),
                        ft.Text(str(val), width=30),
                        ft.IconButton(ft.Icons.REMOVE, on_click=lambda e, a=attr: [p["atributos"].update({a: max(0, p["atributos"][a]-1)}), save_game(), render_details(name)]),
                        ft.IconButton(ft.Icons.ADD, on_click=lambda e, a=attr: [p["atributos"].update({a: p["atributos"][a]+1}), save_game(), render_details(name)]),
                    ])
                )

        elif current_tab == "DOCS":
            content.controls.append(ft.FilledButton(" + NOVO DOC", on_click=lambda _: add_custom_field(name, "documentos")))
            for doc_title, doc_content in p["documentos"].items():
                content.controls.append(
                    ft.Column([
                        ft.Row([
                            ft.IconButton(ft.Icons.DELETE, icon_color="red", on_click=lambda e, t=doc_title: delete_item(name, "documentos", t)),
                            ft.Text(doc_title, weight="bold", expand=True),
                        ]),
                        ft.TextField(value=doc_content, multiline=True, on_change=lambda e, t=doc_title: [p["documentos"].update({t: e.control.value}), save_game()])
                    ])
                )

        main_layout.controls.append(content)
        page.update()

    def set_tab(tab_name, p_name):
        nonlocal current_tab
        current_tab = tab_name
        render_details(p_name)

    render_home()

ft.run(main)
