class Zona:
    def __init__(self, municipio, cod_ine, id_estacion, estacion_referencia):
        """
        Este modelo representa un municipio y su vinculación con una 
        estación meteorológica de la AEMET.
        """
        self.municipio = municipio
        self.cod_ine = cod_ine
        self.id_estacion = id_estacion
        self.estacion_referencia = estacion_referencia

    @staticmethod
    def from_dict(data):
        """
        Método de conveniencia para crear un objeto Zona a partir 
        de una entrada del archivo estacion_por_municipio.json.
        """
        return Zona(
            municipio=data.get("municipio"),
            cod_ine=data.get("cod_ine"),
            id_estacion=data.get("id_estacion"),
            estacion_referencia=data.get("estacion_referencia")
        )

    def to_dict(self):
        """
        Útil si en el futuro necesitas devolver la lista de municipios 
        a través de una API o controlador.
        """
        return {
            "municipio": self.municipio,
            "cod_ine": self.cod_ine,
            "id_estacion": self.id_estacion,
            "estacion_referencia": self.estacion_referencia
        }