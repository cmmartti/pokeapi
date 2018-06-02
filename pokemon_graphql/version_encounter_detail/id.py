class VersionEncounterDetailID(object):
    """A composite ID containing a location_area_id, pokemon_id, and version_id."""

    def __init__(self, location_area_id, pokemon_id, version_id):
        self.location_area_id = location_area_id
        self.pokemon_id = pokemon_id
        self.version_id = version_id

    def encode(self):
        return str(self.location_area_id) + "/" + str(self.pokemon_id) + "/" + str(self.version_id)

    @classmethod
    def decode(cls, encoded):
        area_id, poke_id, vers_id = encoded.split("/")
        return cls(area_id, poke_id, vers_id)

    def __str__(self):
        return self.encode()
