import requests

from decouple import config


class DocumentoProveedorService:

    @staticmethod
    def buscar_dni(numero_documento):
        token = config('DOCUMENT_API_TOKEN', default='')

        if not token:
            return {
                'ok': False,
                'mensaje': 'No se configuró el servicio de consulta.'
            }

        url = f'https://dniruc.apisperu.com/api/v1/dni/{numero_documento}'

        headers = {
            'Authorization': f'Bearer {token}'
        }

        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=10
            )

            if response.status_code != 200:
                return {
                    'ok': False,
                    'mensaje': 'No se encontró información del DNI.'
                }

            data = response.json()

            nombre = data.get('nombres', '')
            apellido_paterno = data.get('apellidoPaterno', '')
            apellido_materno = data.get('apellidoMaterno', '')

            nombre_completo = f'{nombre} {apellido_paterno} {apellido_materno}'.strip()

            return {
                'ok': True,
                'nombre': nombre_completo,
                'direccion': ''
            }

        except requests.RequestException:
            return {
                'ok': False,
                'mensaje': 'No se pudo conectar con el servicio de consulta.'
            }

    @staticmethod
    def buscar_ruc(numero_documento):
        token = config('DOCUMENT_API_TOKEN', default='')

        if not token:
            return {
                'ok': False,
                'mensaje': 'No se configuró el servicio de consulta.'
            }

        url = f'https://dniruc.apisperu.com/api/v1/ruc/{numero_documento}'

        headers = {
            'Authorization': f'Bearer {token}'
        }

        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=10
            )

            if response.status_code != 200:
                return {
                    'ok': False,
                    'mensaje': 'No se encontró información del RUC.'
                }

            data = response.json()

            return {
                'ok': True,
                'nombre': data.get('razonSocial', ''),
                'direccion': data.get('direccion', '')
            }

        except requests.RequestException:
            return {
                'ok': False,
                'mensaje': 'No se pudo conectar con el servicio de consulta.'
            }