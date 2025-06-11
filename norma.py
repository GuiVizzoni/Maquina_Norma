class NormaMachine:
    """
    Simulador para a Máquina Norma conforme especificado.
    """
    def __init__(self):
        self.registers = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0, 'G': 0, 'H': 0}
        self.program = {}
        self.pc = 0  # Program Counter
        self.start_line = 0

    def set_registers(self, initial_values):
        for reg in self.registers:
            self.registers[reg] = 0
            
        for reg, value in initial_values.items():
            if reg.upper() in self.registers:
                try:
                    self.registers[reg.upper()] = int(value)
                except ValueError:
                    print(f"Aviso: Valor inválido para o registrador {reg.upper()}. Usando 0.")
                    self.registers[reg.upper()] = 0
            else:
                print(f"Aviso: Registrador desconhecido '{reg}'. Ignorando.")

    def _parse_line(self, line: str):
        """
        Analisa uma linha do programa no formato:
        - 'faca add A va_para 0'
        - 'se zero B entao va_para 0 senao va_para 2'
        """
        try:
            line_sem_comentarios = line.split('#')[0].strip()

            if not line_sem_comentarios:
                return None, None

            # Exemplo de linha: "1: faca add A va_para 0"
            parts = line_sem_comentarios.split('va_para')
            label_part = parts[0].split(":")[0].strip()  # Pega o número da linha
            label = int(label_part)

            instr_part = parts[0].strip()
            jump = int(parts[1].strip())

            if "faca add" in instr_part:
                reg = instr_part.split('add')[1].strip()
                instruction = {
                    'op': 'ADD',
                    'reg': reg,
                    'jump': jump
                }
            elif "faca sub" in instr_part:
                reg = instr_part.split('sub')[1].strip()
                instruction = {
                    'op': 'SUB',
                    'reg': reg,
                    'jump': jump
                }
            elif "se zero" in instr_part:
                reg = instr_part.split('zero')[1].split()[0].strip()
                jump_true = int(parts[1].split('entao')[1].split()[0].strip())
                jump_false = int(parts[2].strip())
                instruction = {
                    'op': 'IF_ZERO',
                    'reg': reg,
                    'jump_true': jump_true,
                    'jump_false': jump_false
                }
            else:
                raise ValueError(f"Instrução desconhecida na linha {label}.")

            return label, instruction
        except Exception as e:
            print(f"Erro ao analisar a linha: '{line.strip()}'. Detalhe: {e}")
            return None, None

    def load_program(self, filepath: str):
        self.program = {}
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        label, instruction = self._parse_line(line)
                        if label is not None:
                            self.program[label] = instruction
            if not self.program:
                print("Aviso: Nenhum programa carregado. O arquivo pode estar vazio ou mal formatado.")
                return False
            self.start_line = min(self.program.keys())
            return True
        except FileNotFoundError:
            print(f"Erro: Arquivo '{filepath}' não encontrado.")
            return False

    def _print_state(self, note=""):
        regs_to_show = ('A', 'B', 'C', 'D', 'E')
        reg_values = tuple(self.registers[r] for r in regs_to_show)
        instruction_desc = ""
        pc_display = self.pc

        if note == "Entrada de Dados":
            instruction_desc = "M (Entrada de Dados)"
            pc_display = self.start_line
        elif note == "FIM":
            instruction_desc = f"HALT (Desvio para linha inexistente: {self.pc})"
            pc_display = "FIM"
        else:
            instr = self.program.get(self.pc)
            if instr:
                op, reg, jumps = instr['op'], instr['reg'], instr.get('jump', None)
                if op == "ADD":
                    instruction_desc = f"FACA ADD ({reg}) VA_PARA {jumps}"
                elif op == "SUB":
                    instruction_desc = f"FACA SUB ({reg}) VA_PARA {jumps}"
                elif op == "IF_ZERO":
                    instruction_desc = f"SE ZER ({reg}) ENTAO VA_PARA {jumps['jump_true']} SENAO VA_PARA {jumps['jump_false']}"

        print(f"{str(reg_values):<18} | Linha: {str(pc_display):<5} | Instrução: {instruction_desc}")

    def run(self, verbose=True, delay=0.1):
        if not self.program:
            print("Nenhum programa para executar.")
            return

        self.pc = self.start_line
        
        print("-" * 70)
        self._print_state(note="Entrada de Dados")
        time.sleep(delay * 2)

        while self.pc in self.program:
            if verbose:
                self._print_state()
                time.sleep(delay)

            instr = self.program[self.pc]
            op, reg, jumps = instr['op'], instr['reg'], instr.get('jump', None)

            if op == 'ADD':
                self.registers[reg] += 1
                self.pc = jumps
            elif op == 'SUB':
                if self.registers[reg] > 0:
                    self.registers[reg] -= 1
                self.pc = jumps
            elif op == 'IF_ZERO':
                if self.registers[reg] == 0:
                    self.pc = jumps['jump_true']
                else:
                    self.pc = jumps['jump_false']

        print("-" * 70)
        self._print_state(note="FIM")
        print("\nExecução encerrada.")
        print("\nEstado final dos registradores:")
        print(self.registers)
        print("-" * 70)

# Testando a soma em Máquina Norma
