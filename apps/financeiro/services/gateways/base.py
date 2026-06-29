from abc import ABC, abstractmethod
from decimal import Decimal


class GatewayService(ABC):
    """Interface base para gateways de pagamento."""

    @abstractmethod
    def criar_cobranca(self, cobranca) -> dict:
        """
        Cria a cobrança no gateway externo.
        Retorna dict com ao menos 'gateway_id' e 'url_pagamento'.
        """

    @abstractmethod
    def consultar_status(self, gateway_id: str) -> str:
        """
        Consulta o status da cobrança no gateway.
        Retorna o código de status do gateway.
        """

    @abstractmethod
    def cancelar_cobranca(self, gateway_id: str) -> bool:
        """Cancela a cobrança no gateway. Retorna True se sucesso."""
