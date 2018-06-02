class PokemonEncounterID(object):
    """A composite ID containing location_area_id and pokemon_id."""

    def __init__(self, location_area_id, pokemon_id):
        self.location_area_id = location_area_id
        self.pokemon_id = pokemon_id

    def encode(self):
        return str(self.location_area_id) + "/" + str(self.pokemon_id)

    @classmethod
    def decode(cls, encoded):
        area_id, poke_id = encoded.split("/")
        return cls(area_id, poke_id)

    def __str__(self):
        return self.encode()
