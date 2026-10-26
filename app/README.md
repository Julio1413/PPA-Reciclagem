# ReciclaJá Valença

O ReciclaJá Valença é um aplicativo em desenvolvimento para aproximar pessoas que disponibilizam materiais recicláveis de catadores e pontos de coleta. A proposta é facilitar o encaminhamento de recicláveis e incentivar o descarte correto no município de Valença.

Este projeto está em desenvolvimento. Os requisitos abaixo representam o escopo planejado e podem ainda não estar disponíveis na aplicação.

## Objetivos e funcionalidades previstas

- Cadastro e login em uma conta única, sem separar usuários por categoria.
- Mapa interativo para localizar pontos de coleta e fontes de materiais.
- Agendamento de coletas.
- Conteúdos educativos sobre separação e preparação de materiais recicláveis.
- Histórico de materiais coletados ou disponibilizados.
- Avaliações entre as pessoas que participam das coletas e entregas.

## Estado atual

A estrutura atual inclui telas de login e cadastro, navegação para a página inicial e para o mapa, integração de autenticação com Supabase e uso da localização do dispositivo. As demais funcionalidades estão previstas nos requisitos do projeto e podem estar em implementação.

## Tecnologias

- Python 3.10 ou superior
- [Flet](https://flet.dev/) 1.0
- Flet CLI para execução e empacotamento
- Supabase para autenticação e acesso a dados
- Flet Geolocator para recursos de localização

## Como executar

Use Python 3.10 ou superior e tenha o Flet CLI e as dependências do projeto instalados no ambiente Python. Execute os comandos a seguir no diretório `app`.

Inicie o aplicativo para desktop:

```bash
flet run
```

Para executar no navegador:

```bash
flet run --web
```

O aplicativo utiliza serviços do Supabase. As credenciais da aplicação são definidas em `src/Ferramentas/Supabase.py`; não inclua chaves privadas ou credenciais administrativas em commits ou distribuições públicas.

## Testes

Execute a suíte de testes a partir do diretório `app`:

```bash
pytest
```

## Estrutura do projeto

```text
app/
├── src/
│   ├── Ferramentas/   # Autenticação, acesso ao Supabase e utilitários
│   ├── Pages/         # Telas e recursos de interface
│   ├── assets/        # Recursos visuais
│   └── main.py        # Inicialização e rotas do aplicativo
├── tests/             # Testes automatizados
├── pyproject.toml     # Dependências e configurações
└── README.md
```

## Empacotamento

Os comandos abaixo podem ser usados para gerar builds com o Flet. Execute-os no diretório `app`:

```bash
flet build apk -v      # Android
flet build linux -v    # Linux
flet build windows -v  # Windows
flet build web -v      # Web
```

Consulte a [documentação do Flet](https://flet.dev/docs/) para detalhes sobre execução e publicação em cada plataforma.
