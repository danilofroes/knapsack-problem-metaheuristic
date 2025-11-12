import random

class ILS:
    def __init__(self, itens: dict, capacidade_mochila: int):
        self.itens = itens
        self.capacidade_mochila = capacidade_mochila

    def avalicao_ils(self, valor: int, peso: int, taxa_violacao: int = 20):
        if peso > self.capacidade_mochila:
            return valor - ((peso - self.capacidade_mochila) * taxa_violacao)

        return valor

    # def binarizar_lista(solucao: list):


    def desbinarizar_lista(self, solucao: list):
        contador = 0
        cont_valor = 0
        cont_peso = 0
        itens_selecionados = []

        for num in solucao:
            if num == 1:
                cont_peso += self.itens[num]["peso"]
                cont_valor += self.itens[num]["valor"]
                itens_selecionados.append(self.itens[num].keys())

            elif num == 0:
                pass

            else:
                raise ValueError("valor diferente de 0 ou 1")
            
            contador += 1

        return itens_selecionados

    def get_solucao_inicial(self, tipo_solucao: str = "aleatoria"):
        if tipo_solucao == "aleatoria":
            return [random.choice([0, 1]) for _ in range(len(self.itens))]
        
        elif tipo_solucao == "vazia":
            return [0] * len(self.itens)
        
        elif tipo_solucao == "cheia":
            return [1] * len(self.itens)
        
        elif tipo_solucao == "peso":
            return sorted(self.itens.items(), key=lambda x: x[1]["peso"])
        
        else:
            raise ValueError("Tipo de solução desconhecido")

    def ils(solucao_inicial: list, nivel_pertubacao: int = 1, qntd_buscas: int = None):
        qntd_buscas = solucao_inicial.count() if qntd_buscas is None else qntd_buscas

        if solucao_inicial.count() != itens.keys()