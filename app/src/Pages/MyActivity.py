import flet as ft
from Ferramentas import Supabase, Auth
from Pages import Ui



def MinhaAtividade(page):
    sessao = Auth.ObterSessao()
    nome = sessao.get("nome", "pessoa").strip().split()[0]
    email = sessao.get("email")



    # Ferramentas
    def CriarCartaoLocal(local):
            descricao = local.get("Descrição") or "Sem descrição disponível."
            titulo = local.get("Titulo") or "Ponto de coleta"
    
            return ft.Container(
                ink=True,
                on_click=lambda e: Ui.Sheet(
                    e, page
                ),
                data=local,
                padding=Ui.ESPACO_MEDIO,
                border_radius=Ui.RAIO_CARTAO,
                border=ft.Border.all(1, Ui.COR_CONTORNO),
                bgcolor=Ui.COR_SUPERFICIE_ELEVADA,
                content=ft.Column(
                    spacing=Ui.ESPACO_PEQUENO,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Row(
                                    expand=True,
                                    spacing=Ui.ESPACO_PEQUENO,
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.RECYCLING_ROUNDED,
                                            color=Ui.COR_DESTAQUE,
                                            size=24,
                                        ),
                                        ft.Column(
                                            expand=True,
                                            spacing=2,
                                            controls=[
                                                ft.Text(
                                                    titulo,
                                                    size=16,
                                                    weight=ft.FontWeight.BOLD,
                                                    max_lines=1,
                                                    overflow=ft.TextOverflow.ELLIPSIS,
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                                ft.Container(
                                    bgcolor=Ui.COR_DESTAQUE,
                                    border_radius=20,
                                    padding=ft.Padding.only(
                                        left=Ui.ESPACO_PEQUENO,
                                        right=Ui.ESPACO_PEQUENO,
                                        top=8,
                                        bottom=8,
                                    ),
                                    content=ft.Text(
                                        f"Nada",
                                        size=13,
                                        weight=ft.FontWeight.BOLD,
                                        color=Ui.COR_SUPERFICIE_ESCURA,
                                    ),
                                ),
                            ],
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(
                                    descricao,
                                    size=13,
                                    color=Ui.COR_TEXTO_SECUNDARIO,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    expand=True,
                                ),
                                ft.Icon(
                                    ft.Icons.ARROW_FORWARD_ROUNDED,
                                    color=Ui.COR_TEXTO_SECUNDARIO,
                                    size=20,
                                ),
                            ],
                        ),
                    ],
                ),
            )
    
        
        
        
        
    #Lendo as tabelas
    
    reservado = Supabase.LerTabela('PontosColeta', filtros={"ReservadoPor":f'eq.{email}', "Finalizado":"eq.False"})
    ColunaReservado = ft.Column(scroll=ft.ScrollMode.AUTO, controls=[], height=page.height)

    for reserva in reservado:
        ColunaReservado.controls.append(CriarCartaoLocal(reserva))



    disponibilizado = Supabase.LerTabela('PontosColeta', filtros={"EmailCriador":f'eq.{email}', "Finalizado":"eq.False"})
    ColunaDisponibilizado = ft.Column(scroll=ft.ScrollMode.AUTO, controls=[], height=page.height)

    for disponibilizacao in disponibilizado:
        ColunaDisponibilizado.controls.append(CriarCartaoLocal(disponibilizacao))


    finalizado = Supabase.LerTabela('PontosColeta',filtros={"Finalizado": "eq.True","or": f"(ReservadoPor.eq.{email},EmailCriador.eq.{email})",},)
    ColunaFinalizado = ft.Column(scroll=ft.ScrollMode.AUTO, controls=[], height=page.height)

    for operacao in finalizado:
        ColunaFinalizado.controls.append(CriarCartaoLocal(operacao))




    
    




    page.views.append(
        ft.View(
            route="/minhaatividade",
            bgcolor=Ui.CorPagina(page),
            controls=[
                Ui.Cabecalho(
                    page=page,
                    destino='/',
                    icone=ft.Icons.STICKY_NOTE_2_ROUNDED,
                    titulo='Minha Atividade'
                ),
                ft.Text(
                    f"   Sua atividade, {nome}",
                    size=23,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),


                # UI
                ft.Tabs(
                    width=page.width,
                    length=3,
                    selected_index=0,
                    expand=True,

                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        width=page.width,
                        expand=True,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.TabBar(
                                        splash_border_radius=32,
                                        indicator_color=Ui.CorDeFundoSalva(),
                                        label_color=Ui.CorDeFundoSalva(),
                                        width=page.width,
                                        divider_color=ft.Colors.TRANSPARENT,
                                        tabs=[
                                            ft.Tab(
                                                label=ft.Row(
                                                    margin=-5,
                                                    spacing=3,
                                                    controls=[
                                                        ft.Icon(icon=ft.Icons.BLOODTYPE_ROUNDED,size=25),
                                                        ft.Text("Reservado\n por você",size=13,weight=ft.FontWeight.BOLD)
                                                    ]
                                                )
                                            ),                                                    
                                            ft.Tab(
                                                label=ft.Row(
                                                    margin=-5,
                                                    spacing=3,
                                                    controls=[
                                                        ft.Icon(icon=ft.Icons.HISTORY_ROUNDED,size=25),
                                                        ft.Text("Disponibilizado\n por você",size=13,weight=ft.FontWeight.BOLD)
                                                    ]
                                                )
                                            ),                                                    
                                            ft.Tab(
                                                label=ft.Row(
                                                    margin=-5,
                                                    spacing=3,
                                                    controls=[
                                                        ft.Icon(icon=ft.Icons.INFO_ROUNDED,size=25),
                                                        ft.Text("Operações\nfinalizadas",size=13,weight=ft.FontWeight.BOLD)
                                                    ]
                                                )
                                            ),                                                        
                                            ]
                                        ),
                                    ]
                            ),


                            ft.TabBarView(
                                expand=True,
                                controls=[
                                    ft.Container(
                                        padding=5,
                                        expand=True,
                                        content=ft.Column(
                                            controls=[
                                                ft.Divider(),
                                                ColunaReservado,
                                            ]
                                        )
                                    ),
                                    ft.Container(
                                        padding=5,
                                        expand=True,
                                        content=ft.Column(
                                            controls=[
                                                ft.Divider(),
                                                ColunaDisponibilizado,
                                            ]
                                        )
                                    ),
                                    ft.Container(
                                        padding=5,
                                        expand=True,
                                        content=ft.Column(
                                            controls=[
                                                ft.Divider(),
                                                ColunaFinalizado,
                                            ]
                                        )
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
]
        )
    )