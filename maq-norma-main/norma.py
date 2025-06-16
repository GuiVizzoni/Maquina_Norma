import time
import os

class MaquinaNorma:
    def __init__(self):
    # Inicializa os 8 registradores da máquina.
        self.registradores = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0, 'G': 0, 'H': 0}
        self.programa = {}
        self.contador_de_programa = 0
        self.linha_inicial = 0

    def definir_registradores(self, valores_iniciais):
    # Atribui valores aos registradores.
        for registrador in self.registradores:
            self.registradores[registrador] = 0
            
        for registrador, valor in valores_iniciais.items():
            if registrador.upper() in self.registradores:
                try:
                    self.registradores[registrador.upper()] = int(valor)
                except ValueError:
                    print(f"Aviso: Valor inválido para o registrador {registrador.upper()}. Usando 0.")
                    self.registradores[registrador.upper()] = 0
            else:
                print(f"Aviso: Registrador desconhecido '{registrador}'. Ignorando.")

    def _analisar_linha(self, linha: str):
        try:
            linha_sem_comentarios = linha.split('#')[0].strip()
            if not linha_sem_comentarios:
                return None, None

            parte_rotulo, parte_instrucao = linha_sem_comentarios.split(':', 1)
            rotulo = int(parte_rotulo)
            partes = parte_instrucao.strip().split()
            
            op = partes[0].upper()
            reg = partes[1].upper()
            saltos = [int(j) for j in partes[2:]]

            if op not in ["ADD", "SUB", "ZER"]:
                raise ValueError(f"Operação desconhecida '{op}' na linha {rotulo}.")
            if reg not in self.registradores:
                raise ValueError(f"Registrador desconhecido '{reg}' na linha {rotulo}.")
            if op in ["ADD", "SUB"] and len(saltos) != 1:
                raise ValueError(f"Instrução {op} na linha {rotulo} deve ter 1 desvio.")
            if op == "ZER" and len(saltos) != 2:
                raise ValueError(f"Instrução {op} na linha {rotulo} deve ter 2 desvios.")

            return rotulo, {'op': op, 'reg': reg, 'saltos': saltos}
        except Exception as e:
            print(f"Erro ao analisar a linha: '{linha.strip()}'. Detalhe: {e}")
            return None, None

    def carregar_programa(self, caminho_arquivo: str):
    # Lê os programas dos arquivos '.txt'.
        self.programa = {}
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                for linha in f:
                    linha = linha.strip()
                    if linha:
                        rotulo, instrucao = self._analisar_linha(linha)
                        if rotulo is not None:
                            self.programa[rotulo] = instrucao
            if not self.programa:
                print("Aviso: Nenhum programa carregado. O arquivo pode estar vazio ou mal formatado.")
                return False
            self.linha_inicial = min(self.programa.keys())
            return True
        except FileNotFoundError:
            print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
            return False

    def _imprimir_estado(self, observacao=""):
    # Exibe o estado atual dos registradores e a próxima instrução.
        registradores_a_exibir = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')
        valores_registradores = tuple(self.registradores[r] for r in registradores_a_exibir)

        descricao_instrucao = ""
        exibicao_pc = self.contador_de_programa
        
        if observacao == "Entrada de Dados":
            descricao_instrucao = "M (Entrada de Dados)"
            exibicao_pc = self.linha_inicial
        elif observacao == "FIM":
            descricao_instrucao = f"HALT (Desvio para linha inexistente: {self.contador_de_programa})"
            exibicao_pc = "FIM"
        else:
            instrucao = self.programa.get(self.contador_de_programa)
            if instrucao:
                op, reg, saltos = instrucao['op'], instrucao['reg'], instrucao['saltos']
                if op == "ADD":
                    descricao_instrucao = f"FACA ADD ({reg}) VA_PARA {saltos[0]}"
                elif op == "SUB":
                    descricao_instrucao = f"FACA SUB ({reg}) VA_PARA {saltos[0]}"
                elif op == "ZER":
                    descricao_instrucao = f"SE ZER ({reg}) ENTAO VA_PARA {saltos[0]} SENAO VA_PARA {saltos[1]}"

        print(f"{str(valores_registradores):<18} | Linha: {str(exibicao_pc):<5} | Instrução: {descricao_instrucao}")

    def executar(self, detalhado=True, atraso=0.1):
    # Executa o programa carregado.
        if not self.programa:
            print("Nenhum programa para executar.")
            return

        self.contador_de_programa = self.linha_inicial
        
        print("-" * 70)
        self._imprimir_estado(observacao="Entrada de Dados")
        time.sleep(atraso*2)

        while self.contador_de_programa in self.programa:
            if detalhado:
                self._imprimir_estado()
                time.sleep(atraso)

            instrucao = self.programa[self.contador_de_programa]
            op, reg, saltos = instrucao['op'], instrucao['reg'], instrucao['saltos']

            if op == 'ADD':
                self.registradores[reg] += 1
                self.contador_de_programa = saltos[0]
            elif op == 'SUB':
                if self.registradores[reg] > 0:
                    self.registradores[reg] -= 1
                self.contador_de_programa = saltos[0]
            elif op == 'ZER':
                if self.registradores[reg] == 0:
                    self.contador_de_programa = saltos[0]
                else:
                    self.contador_de_programa = saltos[1]
        
        print("-" * 70)
        self._imprimir_estado(observacao="FIM")
        print("\nExecução encerrada.")
        print("\nEstado final dos registradores:")
        print(self.registradores)
        print("-" * 70)

def obter_valores_iniciais(registradores_necessarios):
# Define os valores iniciais que serão inseridos nos registradores.
    valores = {}
    print(f"\nPor favor, insira os valores iniciais.")
    for registrador in registradores_necessarios:
        while True:
            try:
                valor = input(f"  > Valor para o registrador {registrador}: ")
                valores[registrador] = int(valor)
                break
            except ValueError:
                print("    ERRO: Por favor, insira um número inteiro.")
    return valores

def menu_principal():
    maquina = MaquinaNorma()

    programas = {
        "1": {"arquivo": "soma.txt", "regs": ['A', 'B']},
        "2": {"arquivo": "multiplicacao.txt", "regs": ['A', 'B']},
        "3": {"arquivo": "fatorial.txt", "regs": ['A']},
        "4": {"arquivo": "menorque.txt", "regs": ['A', 'B']}
    }

    while True:
        print("\n--- Simulador de Máquina Norma ---")
        print("Escolha o programa para executar:")
        print("1: Soma (C := A + B)")
        print("2: Multiplicação (A := A * B)")
        print("3: Fatorial (B := Fatorial(A))")
        print("4: Menor Que (A < B)")
        print("5: Sair")

        escolha = input("> ")

        if escolha == '5':
            print("Encerrando.")
            break
        
        if escolha in programas:
            info_programa = programas[escolha]
            arquivo_programa = info_programa["arquivo"]

            if not os.path.exists(arquivo_programa):
                print(f"\nERRO FATAL: Arquivo de programa '{arquivo_programa}' não encontrado.")
                print("Certifique-se de que ele está na mesma pasta que o script Python.")
                continue

            valores_iniciais = obter_valores_iniciais(info_programa["regs"])
            
            maquina.definir_registradores(valores_iniciais)
            
            if maquina.carregar_programa(arquivo_programa):
                print("\nIniciando a execução do programa...")
                maquina.executar()
        else:
            print("Opção inválida. Por favor, escolha de 1 a 4.")

if __name__ == "__main__":
    menu_principal()