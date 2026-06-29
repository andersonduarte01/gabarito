import logging

from .base import GatewayService

logger = logging.getLogger(__name__)


class MercadoPagoService(GatewayService):
    """
    Stub do Mercado Pago. Implementação real exige:
    - pip install mercadopago
    - MP_ACCESS_TOKEN em settings/env
    - Criação de preference/payment via API oficial
    """

    def criar_cobranca(self, cobranca) -> dict:
        logger.warning(
            'MercadoPagoService.criar_cobranca: stub — cobranca pk=%s', cobranca.pk
        )
        return {'gateway_id': '', 'url_pagamento': ''}

    def consultar_status(self, gateway_id: str) -> str:
        logger.warning(
            'MercadoPagoService.consultar_status: stub — gateway_id=%s', gateway_id
        )
        return 'pending'

    def cancelar_cobranca(self, gateway_id: str) -> bool:
        logger.warning(
            'MercadoPagoService.cancelar_cobranca: stub — gateway_id=%s', gateway_id
        )
        return False
