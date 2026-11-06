from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .services import SoapServiceError, obtener_pais


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pais_soap(request, iso_code):
    try:
        pais = obtener_pais(iso_code)
    except SoapServiceError:
        return Response(
            {'detail': 'El servicio SOAP de países no está disponible.'},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    if pais is None:
        return Response(
            {'detail': f'No se encontró el país con código {iso_code.upper()}.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response({'fuente': 'SOAP CountryInfoService (zeep)', 'pais': pais})
