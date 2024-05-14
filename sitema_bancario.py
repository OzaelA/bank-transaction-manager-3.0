from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime
import textwrap

class Cliente:

    def __init__(self, endereco):
        self.endereco = endereco
        self.conta = []

    def transacao(self, conta, transacao):
        transacao.registrar(conta)
    
    def add_conta(self, conta):
        self.conta.append(conta)

class Pessoa(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf
        self.contas = []

class Conta:
    def __init__(self, cliente, numero):
        self._saldo = 0
        self._numero = numero
        self._agencia = '0001'
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):  
        return cls(cliente, numero)
    
    @property
    def saldo(self):
        return self._saldo
    
    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico
    
    def sacar(self, valor):
        saldo = self.saldo
        passou_saldo = valor > saldo

        if passou_saldo:
            print(f'\n❌-|-Você não tem saldo suficiente(R${saldo})!')

        elif valor > 0:
            self._saldo -= valor
            print(f'✅-|-Saque de R${valor} realizado com sucesso!')
            return True
        else:
            print('\n❌-|-Valor informado invalido! Ofereça um valor correspondente.') 

        return False
    
    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print(f'✅-|-Depósito de R${valor} realizado com sucesso!')
            print(f'Seu saldo agora é de R${self._saldo}')
        else:
            print("Por favor, insira um valor positivo.")
            return False
        
        return True

class ContaCorrente(Conta):
    def __init__(self, cliente, numero, limite=500, limite_saques=3):
        super().__init__(cliente, numero)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        saques = len(
            [transacao for transacao in self.historico.transacoes if transacao ['Tipo'] == Saque.__name__]
        )

        passou_limite = valor > self.limite
        passou_saques = saques >= self.limite_saques

        if passou_saques:
            print(f'\n❌-|-Você atingiu o limite diário de saques({self.limite_saques})! Tente novamente no próximo dia!')

        elif passou_limite:
            print(f'\n❌-|-O valor do saque passou do limite permitido({self.limite})!')

        else:
            return super().sacar(valor)
        
        return False
    
    def __str__(self):
        return f"""\
        Agência:\t{self.agencia}
        C/C:\t{self.numero}
        Titular:\t{self.cliente.nome}
        """

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes
    
    def add_transacao(self, transacao):
        tipo_transacao = transacao.__class__.__name__
        transacao_dict = {
            'Tipo': tipo_transacao,
            'Valor': transacao.valor,
            'Data': datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        }
        self._transacoes.append(transacao_dict)

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod    
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.add_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso = conta.depositar(self.valor)

        if sucesso:
            conta.historico.add_transacao(self)


def menu_principal():
    menu = '''\n------------------------MENU------------------------\n
            [Z]- Para Sacar
            [X]- Para ver Extrato
            [C]- Para fazer Deposito
            [NC]- Nova Conta
            [NU]- Novo Cliente
            [L]- Lista de Contas
            [S]- Para sair
    =>'''
    return input(textwrap.dedent(menu))

def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n❌-|-Cliente não possui conta!")
        return

    return cliente.contas[0]

def depositar(clientes):    
    cpf = input("💬-|-Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n❌-|-Cliente não encontrado!")
        return

    valor = float(input("💬-|-Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.transacao(conta, transacao)

def sacar(clientes):
    cpf = input("💬-|-Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n❌-|-Cliente não encontrado!")
        return

    valor = float(input("💬-|-Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.transacao(conta, transacao)

def exibir_extrato(clientes):
    cpf = input("💬-|-Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n❌-|-Cliente não encontrado!")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['Tipo']}:\n\tR$ {transacao['Valor']:.2f}"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")

def criar_cliente(clientes):
    cpf = input("💬-|-Informe o CPF (somente número): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n❌-|-Já existe cliente com esse CPF!")
        return

    nome = input("👥-|-Informe o nome completo: ")
    data_nascimento = input("📅-|-Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("💻-|-Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    cliente = Pessoa(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)

    print("\n✅-|-Cliente criado com sucesso!")

def criar_conta(numero_conta, clientes, contas):
    cpf = input("💬-|-Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n❌-|-Cliente não encontrado, fluxo de criação de conta encerrado!")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n✅-|-Conta criada com sucesso!")

def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))

def main():
    clientes = []
    contas = []

    while True:
        opcao = menu_principal()

        if opcao == "C":
            depositar(clientes)

        elif opcao == "Z":
            sacar(clientes)

        elif opcao == "X":
            exibir_extrato(clientes)

        elif opcao == "NU":
            criar_cliente(clientes)

        elif opcao == "NC":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "L":
            listar_contas(contas)

        elif opcao == "S":
            break

        else:
            print("\n❌-|-Operação inválida, por favor selecione novamente a operação desejada.")

main()
