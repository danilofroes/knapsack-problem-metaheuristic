from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, Dict
import random

class Mochila(ABC):
    def __init__(self, itens: Dict[str, Dict[str, int]], capacidade: int):
        self.itens = itens
        self.capacidade = capacidade

        self.nomes_itens = list(itens.keys())
        self.n_itens = len(self.nomes_itens)

        self.melhor_solucao = [0] * self.n_itens 
        self.melhor_valor = None

    def get_solucao(self, tipo_solucao: str = "aleatoria") -> List[int]:
        '''Gera uma solução inicial baseada no tipo especificado'''
        if tipo_solucao == "aleatoria":
            return [random.choice([0, 1]) for _ in range(len(self.itens))]
        
        elif tipo_solucao == "vazia":
            return [0] * len(self.itens)
        
        elif tipo_solucao == "cheia":
            return [1] * len(self.itens)
        
        elif tipo_solucao in ["peso", "valor", "densidade"]:
            solucao = [0] * self.n_itens
            peso_atual = 0

            if tipo_solucao == "peso":
                nomes_ordenados = sorted(self.itens.items(), key=lambda x: (x[1]["peso"], x[1]["valor"]))
            
            elif tipo_solucao == "valor":
                nomes_ordenados = sorted(self.itens.items(), key=lambda x: (x[1]["valor"], -x[1]["peso"]), reverse=True)
            
            elif tipo_solucao == "densidade":
                nomes_ordenados = sorted(self.itens.items(), key=lambda x: (x[1]["densidade"], x[1]["valor"]), reverse=True)
            
            for nome, dados in nomes_ordenados:
                idx = self.nomes_itens.index(nome)
                peso_item = self.itens[nome]["peso"]
                
                if peso_atual + peso_item <= self.capacidade:
                    solucao[idx] = 1
                    peso_atual += peso_item
            
            return solucao

        else:
            raise ValueError("Tipo de solução desconhecido")

    def desbinarizar_solucao(self, solucao: List[int]) -> List[str]:
        '''Converte a solução binária [1, 0...] para nomes de itens'''
        return [list(self.itens.keys())[i] for i, x in enumerate(solucao) if x == 1]
    
class ILS(Mochila):
    def __init__(self, itens: Dict[str, Dict[str, int]], capacidade: int, interacoes: int = 1000, nivel_perturbacao: int = 1, taxa_violacao: int = 20):
        super().__init__(itens, capacidade)
        self.interacoes = interacoes
        self.nivel_perturbacao = nivel_perturbacao
        self.taxa_violacao = taxa_violacao

    def avaliar_solucao(self, solucao: List[int]) -> Tuple[int, int, int]:
        '''Avalia a solução retornando valor total, peso total e valor penalizado'''
        valor_total = 0
        peso_total = 0

        for i, bit in enumerate(solucao):
            if bit == 1:
                item = list(self.itens.values())[i]
                valor_total += item["valor"]
                peso_total += item["peso"]

        if peso_total > self.capacidade:
            avaliacao = valor_total - ((peso_total - self.capacidade) * self.taxa_violacao)
        else:
            avaliacao = valor_total

        return valor_total, peso_total, avaliacao

    def perturbar_solucao(self, solucao: List[int]) -> List[int]:
        '''Perturba a solução invertendo bits aleatórios'''
        nova_solucao = solucao.copy()
        indices = random.sample(range(len(solucao)), self.nivel_perturbacao)

        for idx in indices:
            nova_solucao[idx] = 1 - nova_solucao[idx]

        return nova_solucao

    def busca_local(self, solucao_inicial: List[int]) -> Tuple[List[int], float]:
        solucao_atual = solucao_inicial[:]
        _, _, aval_atual = self.avaliar_solucao(solucao_atual)
        
        vizinho_candidato = None
        aval_candidato = -float('inf')

        for i in range(self.n_itens):
            vizinho = solucao_atual[:]
            vizinho[i] = 1 - vizinho[i]
            _, _, aval = self.avaliar_solucao(vizinho)
            
            if aval > aval_candidato:
                aval_candidato = aval
                vizinho_candidato = vizinho[:]
        
        if aval_candidato > aval_atual:
            print(f"[Busca Local] 1 passo realizado: {aval_atual} -> {aval_candidato}", end="\n\n")
            return vizinho_candidato, aval_candidato
        
        print(f"[Busca Local] Nenhuma melhora. Avaliação: {aval_atual}", end="\n\n")

        return solucao_atual, aval_atual
    
    def executar_ils(self, tipo_solucao_inicial: str = "aleatoria") -> Tuple[List[int], float]:
        print(f"--- Iniciando ILS (Capacidade: {self.capacidade}) ---")
        
        solucao_atual = self.get_solucao(tipo_solucao_inicial)
        _, _, aval_inicial = self.avaliar_solucao(solucao_atual)
        print(f"Solução Inicial Gerada: {aval_inicial}", end="\n\n")
        
        solucao_atual, aval_atual = self.busca_local(solucao_atual)
        
        self.melhor_solucao = solucao_atual[:]
        self.melhor_valor = aval_atual

        print(f"Solução Inicial Melhorada: Valor {aval_atual}", end="\n\n")

        for i in range(self.interacoes):
            solucao_perturbada = self.perturbar_solucao(solucao_atual)
            print(f"Solução Perturbada na iteração {i}")
            print(f"   Avaliação antes da busca local: {self.avaliar_solucao(solucao_perturbada)[2]}")
            solucao_busca_local, aval_busca_local = self.busca_local(solucao_perturbada)
            
            if aval_busca_local > aval_atual:
                solucao_atual = solucao_busca_local[:]
                aval_atual = aval_busca_local
                
                if aval_busca_local > self.melhor_valor:
                    self.melhor_solucao = solucao_busca_local[:]
                    self.melhor_valor = aval_busca_local
                    print(f"Iteração {i}: Nova melhor solução encontrada -> {self.melhor_valor}")

        return self.melhor_solucao, self.melhor_valor