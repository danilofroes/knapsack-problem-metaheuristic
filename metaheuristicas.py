from abc import ABC, abstractmethod
from typing import List, Tuple, Dict
import random
import math
import matplotlib.pyplot as plt
import numpy as np

class KnapsackProblem(ABC):
    def __init__(self, itens: Dict[str, Dict[str, int]], capacidade: int, seed: int = 42, str_peso: str = "peso", str_valor: str = "valor"):
        random.seed(seed)

        for item in itens:
            peso = itens[item][str_peso]
            valor = itens[item][str_valor]
            densidade = valor / peso if peso > 0 else 0
            itens[item]["densidade"] = densidade

        self.itens = itens
        self.capacidade = capacidade
        self.nomes_itens = list(itens.keys())

        # self.pesos = [item[str_peso] for item in itens.values()]
        # self.valores = [item[str_valor] for item in itens.values()]
        # self.densidades = [valor / peso if peso > 0 else 0 
        #                    for valor, peso in zip(self.valores, self.pesos)]

        self.n_itens = len(self.nomes_itens)

        self.melhor_solucao = [0] * self.n_itens 
        self.melhor_valor = -float('inf')

        self.str_peso = str_peso
        self.str_valor = str_valor 

        self.resultados_gulosos = {}

    def solucao_gulosa(self, tipo_solucao: str, isDesensidade: bool = False):
        total = 0
        soma_valores = 0

        if tipo_solucao == self.str_peso or tipo_solucao == "peso":
            itens_ordenados = sorted(self.itens.items(), key=lambda x: (x[1][self.str_peso], x[1][self.str_valor]))
            nome_metodo = "Guloso (Tempo)"

        elif tipo_solucao == self.str_valor or tipo_solucao == "valor":
            itens_ordenados = sorted(self.itens.items(), key=lambda x: (x[1][self.str_valor], -x[1][self.str_peso]), reverse=True)
            nome_metodo = "Guloso (Lucro)"

        elif tipo_solucao == "densidade":
            itens_ordenados = sorted(self.itens.items(), key=lambda x: (x[1]["densidade"], x[1][self.str_valor]), reverse=True)
            nome_metodo = "Guloso (Densidade)"

        else:
            print("Tipo inválido")
            return

        while total < self.capacidade:
            for item in itens_ordenados:
                nome_item = item[0]
                peso_item = item[1][self.str_peso]
                valor_item = item[1][self.str_valor]
                densidade_item = round(item[1]["densidade"], 2) if isDesensidade else None

                if total + peso_item <= self.capacidade:
                    total += peso_item
                    soma_valores += valor_item
                    print(f'Adicionando {nome_item} ({self.str_peso}: {peso_item} | {self.str_valor}: {valor_item}', end='')
                    print(f' | densidade: {densidade_item}' if isDesensidade else '', end='')
                    print(f') | Total atual: {total}', end='\n\n')
            break

        self.resultados_gulosos[nome_metodo] = {
            "valor": soma_valores,
            "peso": total,
            "ocupacao": (total / self.capacidade) * 100
        }

        print(f'[{nome_metodo}] Valor Final: {soma_valores} | Peso Usado: {total}')

        return soma_valores, total

    def get_solucao(self, tipo_solucao: str = "aleatoria") -> List[int]:
        '''Gera uma solução inicial baseada no tipo especificado'''
        if tipo_solucao == "aleatoria":
            return [random.choice([0, 1]) for _ in range(len(self.itens))]
        
        elif tipo_solucao == "vazia":
            return [0] * len(self.nomes_itens)
        
        elif tipo_solucao == "cheia":
            return [1] * len(self.nomes_itens)
        
        elif tipo_solucao in ["peso", "valor", "densidade", self.str_peso, self.str_valor]:
            solucao = [0] * self.n_itens
            peso_atual = 0

            if tipo_solucao == self.str_peso or tipo_solucao == "peso":
                nomes_ordenados = sorted(self.itens.items(), key=lambda x: (x[1][self.str_peso], x[1][self.str_valor]))
            
            elif tipo_solucao == self.str_valor or tipo_solucao == "valor":
                nomes_ordenados = sorted(self.itens.items(), key=lambda x: (x[1][self.str_valor], -x[1][self.str_peso]), reverse=True)
            
            elif tipo_solucao == "densidade":
                nomes_ordenados = sorted(self.itens.items(), key=lambda x: (x[1]["densidade"], x[1][self.str_valor]), reverse=True)

            for nome, _ in nomes_ordenados:
                idx = self.nomes_itens.index(nome)

                peso_item = self.itens[nome][self.str_peso]

                if peso_atual + peso_item <= self.capacidade:
                    solucao[idx] = 1
                    peso_atual += peso_item

            return solucao

        else:
            raise ValueError(f"Tipo de solução '{tipo_solucao}' desconhecido")

    def desbinarizar_solucao(self, solucao: List[int]) -> List[str]:
        '''Converte a solução binária [1, 0...] para nomes de itens'''
        return [self.nomes_itens[i] for i, bit in enumerate(solucao) if bit == 1]
    
    def avaliar_solucao(self, solucao: List[int], taxa_violacao: int = 20) -> Tuple[int, int, int]:
        '''Avalia a solução retornando valor total, peso total e valor penalizado'''
        valor_total = 0
        peso_total = 0

        for i, bit in enumerate(solucao):
            if bit == 1:
                item = list(self.itens.values())[i]
                valor_total += item[self.str_valor]
                peso_total += item[self.str_peso]

        if peso_total > self.capacidade:
            excecao = peso_total - self.capacidade
            avaliacao = valor_total - (excecao * taxa_violacao)

        else:
            avaliacao = valor_total

        return valor_total, peso_total, avaliacao
    
class ILS(KnapsackProblem):
    def __init__(self, itens: Dict[str, Dict[str, int]], capacidade: int, 
                 interacoes: int = 1000, 
                 nivel_perturbacao: int = 1, 
                 taxa_violacao: int = 20,
                 limite_sem_melhora: int = 50,
                 seed: int = 42,
                 str_peso: str = "peso", 
                 str_valor: str = "valor"):
        
        super().__init__(itens, capacidade, seed, str_peso, str_valor)

        self.interacoes = interacoes
        self.nivel_perturbacao = nivel_perturbacao
        self.taxa_violacao = taxa_violacao
        self.limite_sem_melhora = limite_sem_melhora

        self.str_peso = str_peso
        self.str_valor = str_valor

        self.historico_ils = []
        self.tempo_final_ils = 0

    def perturbar_solucao(self, solucao: List[int]) -> List[int]:
        nova_solucao = solucao[:]
        
        indices_um = [i for i, x in enumerate(solucao) if x == 1]
        indices_zero = [i for i, x in enumerate(solucao) if x == 0]
        
        qnt_remover = min(len(indices_um), self.nivel_perturbacao // 2)
        qnt_adicionar = self.nivel_perturbacao - qnt_remover
        
        indices_para_inverter = []
        
        if indices_um:
            indices_para_inverter.extend(random.sample(indices_um, qnt_remover))
        
        if indices_zero:
            indices_para_inverter.extend(random.sample(indices_zero, qnt_adicionar))
            
        if not indices_para_inverter:
             indices_para_inverter = random.sample(range(self.n_itens), self.nivel_perturbacao)

        for idx in indices_para_inverter:
            nova_solucao[idx] = 1 - nova_solucao[idx]

        return nova_solucao

    def busca_local(self, solucao_inicial: List[int]) -> Tuple[List[int], int]:
        solucao_atual = solucao_inicial[:] 
        _, _, aval_atual = self.avaliar_solucao(solucao_atual, self.taxa_violacao)
        
        melhor_vizinho = None
        aval_vizinho = -float('inf')

        for i in range(self.n_itens):
            vizinho = solucao_atual[:]
            vizinho[i] = 1 - vizinho[i]
            _, _, aval = self.avaliar_solucao(vizinho, self.taxa_violacao)

            if aval > aval_vizinho:
                aval_vizinho = aval
                melhor_vizinho = vizinho[:]

        if aval_vizinho > aval_atual:
            print(f"[Busca Local] 1 passo realizado: {aval_atual} -> {aval_vizinho}", end="\n\n")
            return melhor_vizinho, aval_vizinho

        print(f"[Busca Local] Nenhuma melhora. Avaliação: {aval_atual}", end="\n\n")

        return solucao_atual, aval_atual
    
    def executar_ils(self, tipo_solucao_inicial: str = "aleatoria") -> Tuple[List[int], int]:
        print(f"--- Iniciando ILS (Capacidade: {self.capacidade}) ---")

        self.historico_ils = []

        solucao_atual = self.get_solucao(tipo_solucao_inicial)
        _, _, aval_inicial = self.avaliar_solucao(solucao_atual, self.taxa_violacao)
        print(f"Solução Inicial Gerada: {aval_inicial}", end="\n\n")

        solucao_atual, aval_atual = self.busca_local(solucao_atual)

        self.melhor_solucao = solucao_atual[:]
        self.melhor_valor = aval_atual

        self.historico_ils.append(self.melhor_valor)

        print(f"Solução Inicial (pós busca local): {aval_atual}")

        contador_sem_melhora = 0

        for i in range(self.interacoes):
            solucao_perturbada = self.perturbar_solucao(solucao_atual)
            solucao_candidata, aval_candidata = self.busca_local(solucao_perturbada)

            if aval_candidata > aval_atual:
                solucao_atual = solucao_candidata[:]
                aval_atual = aval_candidata

            if aval_candidata > self.melhor_valor:
                self.melhor_solucao = solucao_candidata[:]
                self.melhor_valor = aval_candidata
                print(f"Iteração {i}: NOVO RECORDE -> {self.melhor_valor}", end="\n\n")
                contador_sem_melhora = 0

            else:
                contador_sem_melhora += 1

            self.historico_ils.append(self.melhor_valor)

            if contador_sem_melhora >= self.limite_sem_melhora:
                print(f"\n[PARADA] O algoritmo estagnou por {self.limite_sem_melhora} iterações e parou na iteração {i}.")
                restante = self.interacoes - 1 - i
                self.historico_ils.extend([self.melhor_valor] * restante)
                break

        print(f"\nFim do ILS. Melhor valor encontrado: {self.melhor_valor}")

        _, peso_final, _ = self.avaliar_solucao(self.melhor_solucao, self.taxa_violacao)
        self.tempo_final_ils = peso_final

        return self.melhor_solucao, self.melhor_valor
    
    def plotar_convergencia(self):
        """Plota a curva de evolução do ILS após a execução"""
        if not self.historico_ils:
            print("Erro: Execute o ILS primeiro.")
            return
        
        plt.figure(figsize=(10, 5))
        plt.plot(self.historico_ils, label='Melhor Solução Global', color='#2980b9', linewidth=2)
        plt.title('Curva de Convergência (ILS)', fontsize=14)
        plt.xlabel('Iterações', fontsize=12)
        plt.ylabel('Valor da Função Objetivo (Lucro)', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        plt.show()

    def plotar_comparativo_lucro(self):
        """Compara o lucro do ILS com os gulosos salvos"""
        metodos = list(self.resultados_gulosos.keys()) + ["Metaheurística (ILS)"]
        lucros = [d['valor'] for d in self.resultados_gulosos.values()] + [self.melhor_valor]
        
        plt.figure(figsize=(10, 5))
        barras = plt.bar(metodos, lucros, color=['gray']*len(self.resultados_gulosos) + ['#27ae60'])
        
        plt.title('Comparativo de Lucro Total', fontsize=14)
        plt.ylabel('Lucro (R$)', fontsize=12)
        
        for barra in barras:
            altura = barra.get_height()
            plt.text(barra.get_x() + barra.get_width()/2., altura,
                     f'{int(altura)}', ha='center', va='bottom', fontweight='bold')
        
        plt.ylim(0, max(lucros) * 1.15)
        plt.show()

    def plotar_eficiencia_tempo(self):
        """Compara o tempo utilizado vs capacidade"""
        metodos = list(self.resultados_gulosos.keys()) + ["Metaheurística (ILS)"]
        tempos = [d['peso'] for d in self.resultados_gulosos.values()] + [self.tempo_final_ils]
        
        plt.figure(figsize=(10, 5))
        plt.bar(metodos, tempos, color='#3498db', width=0.5)
        plt.axhline(y=self.capacidade, color='red', linestyle='--', label=f'Turno ({self.capacidade} min)')
        
        plt.title('Eficiência de Ocupação do Turno', fontsize=14)
        plt.ylabel('Tempo Utilizado (min)', fontsize=12)
        plt.legend()
        
        for i, tempo in enumerate(tempos):
            pct = (tempo / self.capacidade) * 100
            plt.text(i, tempo + 5, f'{pct:.1f}%', ha='center', fontweight='bold')
            
        plt.ylim(0, max(max(tempos), self.capacidade) * 1.15)
        plt.show()
    
# class SimulatedAnnealing(KnapsackProblem):
#     def __init__(self, itens: Dict[str, Dict[str, int]], capacidade: int, 
#                  temperatura_inicial: float, 
#                  taxa_decaimento: float, 
#                  temperatura_final: float = None):
#         super().__init__(itens, capacidade)
#         self.temperatura_inicial = temperatura_inicial
#         self.temperatura_final = temperatura_final
#         self.taxa_decaimento = taxa_decaimento
    
#     @staticmethod
#     def get_prob_aceitacao(nova_solucao: int, solucao_atual: int, temp: float) -> float:
#         """Calcula a probabilidade de aceitação de uma nova solução"""
#         delta_solucao = nova_solucao - solucao_atual

#         if delta_solucao > 0:
#             return float(nova_solucao)
        
#         else:
#             return math.exp(-delta_solucao / temp)
