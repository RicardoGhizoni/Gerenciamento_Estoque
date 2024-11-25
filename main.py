import json
from datetime import datetime
from colorama import Fore, Style

# Estruturas de dados para armazenar o estoque e movimentações
estoque = {}
movimentacoes = []

# Categorias válidas para o sistema
categorias_validas = [
    "Celulares", "Computadores", "Periféricos",
    "Consoles", "Jogos", "Acessórios Gamer",
    "Câmeras", "Áudio e Vídeo", "Outros"
]

# Função: Carregar dados dos arquivos JSON
def carregar_dados():
    """
    Carrega os dados de estoque e movimentações de arquivos JSON,
    ou cria novas estruturas vazias caso os arquivos não existam ou estejam corrompidos.
    """
    global estoque, movimentacoes
    try:
        with open("estoque.json", "r") as arquivo_estoque:
            conteudo_estoque = arquivo_estoque.read()
            estoque = json.loads(conteudo_estoque) if conteudo_estoque.strip() else {}
        print("Estoque carregado com sucesso!")
    except FileNotFoundError:
        print("Erro ao ler o arquivo 'estoque.json'. Criando novo estoque...")
        estoque = {}
    except json.JSONDecodeError:
        print("Erro: O arquivo 'estoque.json' está corrompido. Criando novo estoque...")
        estoque = {}

    try:
        with open("movimentacoes.json", "r") as arquivo_movimentacoes:
            conteudo_movimentacoes = arquivo_movimentacoes.read()
            movimentacoes = json.loads(conteudo_movimentacoes) if conteudo_movimentacoes.strip() else []
        print("Movimentações carregadas com sucesso!")
    except FileNotFoundError:
        print("Arquivo 'movimentacoes.json' não encontrado. Criando nova lista de movimentações...")
        movimentacoes = []
    except json.JSONDecodeError:
        print("Erro: O arquivo 'movimentacoes.json' está corrompido. Criando nova lista de movimentações...")
        movimentacoes = []

# Função: Salvar dados nos arquivos JSON
def salvar_dados():
    """
    Salva os dados de estoque e movimentações em arquivos JSON para persistência.
    """
    with open("estoque.json", "w") as arquivo_estoque:
        json.dump(estoque, arquivo_estoque, indent=4)
    with open("movimentacoes.json", "w") as arquivo_movimentacoes:
        json.dump(movimentacoes, arquivo_movimentacoes, indent=4)
    print("Dados salvos com sucesso!")

# Função: Formatar localização para exibição
def formatar_localizacao(localizacao):
    """
    Formata a localização do produto para exibição legível no relatório.
    """
    return (
        f"    Setor: {localizacao['setor']}\n"
        f"    Prateleira: {localizacao['prateleira']}\n"
        f"    Nível: {localizacao['nivel']}"
    )

# Função: Cadastrar um novo produto no sistema
def cadastrar_produto():
    """
    Cadastra um novo produto no estoque, validando as informações inseridas pelo usuário.
    """
    print("== Cadastro de Produto ==")
    codigo = input("Código do produto: ")
    if codigo in estoque:
        print(f"O produto com o código '{codigo}' já está cadastrado. Tente novamente.\n")
        return

    nome = input("Nome do produto: ")
    categoria = input(f"Categoria do produto (Escolha entre {', '.join(categorias_validas)}): ")
    if categoria not in categorias_validas:
        print(f"Categoria inválida. Escolha entre: {', '.join(categorias_validas)}\n")
        return

    quantidade = int(input("Quantidade em estoque: "))
    preco = float(input("Preço do produto: "))
    setor = input("Setor no depósito: ")
    prateleira = input("Prateleira no depósito: ")
    nivel = input("Nível na prateleira: ")

    estoque[codigo] = {
        "nome": nome,
        "categoria": categoria,
        "quantidade": quantidade,
        "preco": preco,
        "localizacao": {
            "setor": setor,
            "prateleira": prateleira,
            "nivel": nivel
        }
    }
    print(f"Produto '{nome}' cadastrado com sucesso!\n")
    salvar_dados()

# Função: Registrar entrada de produtos no estoque
def registrar_entrada():
    """
    Registra a entrada de produtos no estoque e adiciona a movimentação ao histórico.
    """
    print("== Registrar Entrada ==")
    codigo = input("Código do produto: ")
    if codigo not in estoque:
        print(f"Produto com código '{codigo}' não encontrado no estoque.\n")
        return

    quantidade = int(input("Quantidade recebida: "))
    estoque[codigo]["quantidade"] += quantidade

    movimentacoes.append({
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo": "Entrada",
        "nome": estoque[codigo]["nome"],
        "quantidade": quantidade
    })
    print(f"Movimentação registrada: Entrada de {quantidade} unidade(s) do produto '{estoque[codigo]['nome']}'.\n")
    salvar_dados()

# Função: Registrar saída de produtos no estoque
def registrar_saida():
    """
    Registra a saída de produtos do estoque e adiciona a movimentação ao histórico.
    """
    print("== Registrar Saída ==")
    codigo = input("Código do produto: ")
    if codigo not in estoque:
        print(f"Produto com código '{codigo}' não encontrado no estoque.\n")
        return

    quantidade = int(input("Quantidade vendida: "))
    if quantidade > estoque[codigo]["quantidade"]:
        print("Erro: Quantidade em estoque insuficiente.\n")
        return

    estoque[codigo]["quantidade"] -= quantidade

    movimentacoes.append({
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo": "Saída",
        "nome": estoque[codigo]["nome"],
        "quantidade": quantidade
    })
    print(f"Movimentação registrada: Saída de {quantidade} unidade(s) do produto '{estoque[codigo]['nome']}'.\n")
    salvar_dados()

# Função: Gerar relatórios de estoque
def gerar_relatorios():
    """
    Gera relatórios do estoque, destacando produtos em falta, baixo estoque e excesso,
    e exibindo histórico de movimentações.
    """
    print("\n=== RELATÓRIO DE ESTOQUE ===\n")

    # Produtos em falta
    print(Fore.RED + "-- PRODUTOS EM FALTA --" + Style.RESET_ALL)
    produtos_em_falta = [p for p in estoque.values() if p["quantidade"] == 0]
    if produtos_em_falta:
        for produto in produtos_em_falta:
            print(f"- {produto['nome']} | Código: {produto['codigo']}")
    else:
        print("Nenhum produto em falta.\n")

    # Produtos com estoque baixo
    print(Fore.YELLOW + "-- PRODUTOS COM ESTOQUE BAIXO --" + Style.RESET_ALL)
    limite_baixo = int(input("Informe o limite para estoque baixo: "))
    for codigo, produto in estoque.items():
        if produto["quantidade"] < limite_baixo:
            print(f"- {produto['nome']} | Código: {codigo} | Quantidade: {produto['quantidade']}")
            print(f"  Localização:\n{formatar_localizacao(produto['localizacao'])}")

    # Produtos com excesso de estoque
    print(Fore.GREEN + "-- PRODUTOS COM EXCESSO DE ESTOQUE --" + Style.RESET_ALL)
    limite_excesso = int(input("Informe o limite para excesso de estoque: "))
    for codigo, produto in estoque.items():
        if produto["quantidade"] > limite_excesso:
            print(f"- {produto['nome']} | Código: {codigo} | Quantidade: {produto['quantidade']}")
            print(f"  Localização:\n{formatar_localizacao(produto['localizacao'])}")

    # Histórico de movimentações
    print("\n-- HISTÓRICO DE MOVIMENTAÇÕES --")
    if movimentacoes:
        for movimentacao in movimentacoes:
            print(f"{movimentacao['data']} | {movimentacao['tipo']} | {movimentacao['nome']} | Quantidade: {movimentacao['quantidade']}")
    else:
        print("Nenhuma movimentação registrada.")

    print("\nRelatório concluído.\n")

# Função: Pesquisar produtos no estoque
def pesquisar_produto():
    """
    Permite pesquisar produtos no estoque por código ou nome, exibindo detalhes relevantes.
    """
    print("== Pesquisa de Produtos ==")
    termo = input("Digite o código ou o nome do produto: ").lower()
    resultados = [
        {"codigo": codigo, **produto} for codigo, produto in estoque.items()
        if termo in produto["nome"].lower() or termo in codigo
    ]

    if not resultados:
        print("Nenhum produto encontrado com o termo informado.\n")
        return

    for produto in resultados:
        print(f"""
=== Detalhes do Produto ===
Código: {produto['codigo']}
Descrição: {produto['nome']}
Categoria: {produto['categoria']}
Quantidade em Estoque: {produto['quantidade']}
Valor Unitário: R${produto['preco']:.2f}
Valor Total em Estoque: R${produto['preco'] * produto['quantidade']:.2f}
Localização:
{formatar_localizacao(produto['localizacao'])}
        """)

# Menu principal
def menu():
    """
    Exibe o menu principal do sistema e gerencia a interação com o usuário.
    """
    while True:
        print("==== Sistema de Gerenciamento de Estoque ====")
        print("1. Cadastrar Produto")
        print("2. Registrar Entrada")
        print("3. Registrar Saída")
        print("4. Gerar Relatórios")
        print("5. Pesquisar Produto")
        print("6. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cadastrar_produto()
        elif opcao == "2":
            registrar_entrada()
        elif opcao == "3":
            registrar_saida()
        elif opcao == "4":
            gerar_relatorios()
        elif opcao == "5":
            pesquisar_produto()
        elif opcao == "6":
            salvar_dados()
            print("Saindo do sistema. Até mais!")
            break
        else:
            print("Opção inválida. Tente novamente.\n")

# Inicialização do sistema
if __name__ == "__main__":
    carregar_dados()
    menu()
