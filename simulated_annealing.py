from math import exp

class SimulatedAnnealing:
    def __init__(self, temperatura_inicial: float, taxa_decaimento: float, temperatura_final: float = None):
        self.temperatura_inicial = temperatura_inicial
        self.temperatura_final = temperatura_final
        self.taxa_decaimento = taxa_decaimento
    
    @staticmethod
    def _get_prob_aceitacao(nova_solucao: int, solucao_atual: int, temp: float) -> float:
        """Calcula a probabilidade de aceitação de uma nova solução"""
        delta_solucao = nova_solucao - solucao_atual

        if delta_solucao > 0:
            return float(nova_solucao)
        
        else:
            return exp(-delta_solucao / temp)
