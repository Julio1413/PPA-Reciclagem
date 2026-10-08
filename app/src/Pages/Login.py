import flet as ft
from Ferramentas import Ferramentas, Auth
from Pages import Ui
import re

print('='*20)
print('Login')


def ValidarNome(nome):
    return re.fullmatch(r"[A-Za-zÀ-ÿ\s]{2,}", nome.strip()) is not None 

def ValidarEmail(email):
    return re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email.strip()) is not None


def Login(page):
    senha = ft.TextField(label='Senha',border_radius=32,width=page.width, password=True, can_reveal_password=True)
    email = ft.TextField(label='E-mail',border_radius=32,width=page.width,keyboard_type=ft.KeyboardType.EMAIL)


    def Entrar():
        if len(senha.value) >= 10 and ValidarEmail(email.value) :
            #Entrafa
            tentativa = Auth.LoginUsuario(email=email.value,senha=senha.value)

            if tentativa == 0:
                page.show_dialog(ft.SnackBar(ft.Text('Login realizada com sucesso!!',weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.GREEN))
                Ui.IrPara(rota='/',page=page)

            elif tentativa ==1:
                page.show_dialog(ft.SnackBar(ft.Text('E-mail ou senha incorretos!',weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.RED))
            else:
                page.show_dialog(ft.SnackBar(ft.Text('Ocorreu um erro desconhecido.',weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.RED))




    page.views.append(
        ft.View(
            bgcolor=Ui.CorDeFundoSalva(),
            route='/cadastro',
            controls=[
                Ui.Cabecalho(
                    page=page,
                    titulo='Entrar',
                    destino='/login1',
                    icone_btn=ft.Icons.LOGIN_ROUNDED,
                ),
                Ui.Container(
                    scroll='none',
                    page=page,
                    controles=[
                        email,
                        senha,
                        ft.Placeholder(expand=True,color=ft.Colors.TRANSPARENT),
                        ft.Button(
                            on_click=lambda _: Entrar(),
                            width=page.width,
                            height=50,
                            bgcolor=ft.Colors.GREEN,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Text('Entrar',color=ft.Colors.WHITE,size=20,weight=ft.FontWeight.BOLD)
                                ]
                            )
                        ),
                    ]
                ),
            ]
        )
    )
    page.update()
    


def Cadastro(page):

    senha = ft.TextField(label='Senha',border_radius=32,width=page.width, password=True, can_reveal_password=True)
    nome = ft.TextField(label='Nome',border_radius=32,width=page.width,keyboard_type=ft.KeyboardType.NAME)
    email = ft.TextField(label='E-mail',border_radius=32,width=page.width,keyboard_type=ft.KeyboardType.EMAIL)

    def Cadastro():
      
        if len(senha.value) >= 10 and ValidarEmail(email.value) and ValidarNome(nome.value):
            #Cadastro
            tentativa = Auth.CadastrarUsuario(email=email.value,senha=senha.value,nome=nome.value)

            if tentativa == 0:
                page.show_dialog(ft.SnackBar(ft.Text('Criação de conta realizada com sucesso!!',weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.GREEN))
                Ui.IrPara(rota='/',page=page)

            elif tentativa ==1:
                page.show_dialog(ft.SnackBar(ft.Text('Email já cadastrado! Tente entrar!\nSua senha deve conter pelo menos 10 caracteres!',weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.RED))
            else:
                page.show_dialog(ft.SnackBar(ft.Text('Ocorreu um erro desconhecido.',weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.RED))




        else:
            page.show_dialog(ft.SnackBar(ft.Text('Preencha todos os campos corretamente!\nSua senha deve conter pelo menos 10 caracteres!',weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.RED))

    page.views.append(
        ft.View(
            bgcolor=Ui.CorDeFundoSalva(),
            route='/login1',
            controls=[
                Ui.Cabecalho(
                    page=page,
                    titulo='Cadastro',
                    destino='/cadastro',
                    icone_btn=ft.Icons.LOGIN_ROUNDED,
                ),
                Ui.Container(
                    page=page,
                    scroll='none',
                    controles=[
                        nome,
                        email,
                        senha,
                        ft.Placeholder(expand=True,color=ft.Colors.TRANSPARENT),
                        ft.Button(
                            on_click=lambda _: Cadastro(),
                            width=page.width,
                            height=50,
                            bgcolor=ft.Colors.GREEN,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Text('Entrar',color=ft.Colors.WHITE,size=20,weight=ft.FontWeight.BOLD)
                                ]
                            )
                        ),

                    ]
                ),

            ]
        )
    )
    page.update()




def PaginaLogin(page):
    #Botões
    login = ft.Button(
        on_click=lambda _: Ui.IrPara('/login1',page),
        width=page.width,
        height=50,
        bgcolor=ft.Colors.GREEN,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text('Entrar',color=ft.Colors.WHITE,size=20,weight=ft.FontWeight.BOLD)
            ]
        )
    )
    cadastro = ft.Button(
        on_click=lambda _: Ui.IrPara('/cadastro',page),
        width=page.width,
        height=50,
        bgcolor=ft.Colors.GREEN,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text('Cadastro',color=ft.Colors.WHITE,size=20,weight=ft.FontWeight.BOLD)
            ]
        )
    )


    page.title = f'{Ui.NomeDoApp()} - Login'
    page.views.append(
        ft.View(
            route='/login',
            bgcolor=Ui.CorDeFundoSalva(),
            controls=[
                #Cabeçalho
                Ui.Cabecalho(
                    page=page,
                    titulo='Login',
                    destino='/login',
                    icone_btn=ft.Icons.LOGIN_ROUNDED,
                ),
                
                ft.Placeholder(color=ft.Colors.TRANSPARENT,height=5),
                Ui.Container(
                    scroll='none',
                    tamanho=page.height*0*2,                   page=page,
                    controles=[
                        ft.Container(
                            bgcolor=ft.Colors.with_opacity(0.2,ft.Colors.BLACK),
                            border_radius=32,
                            align=ft.Alignment.CENTER,
                            content=ft.Image(src='banner_alternativo.png')
                        ),
                        ft.Placeholder(color=ft.Colors.TRANSPARENT,expand=True),
                        login,
                        cadastro
                    ]
                )
            ]
        )
    )