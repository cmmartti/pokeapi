from graphene import List, String


class TranslationList(List):

    def __init__(self, type, *args, **kwargs):
        kwargs.setdefault("lang", String())
        super(TranslationList, self).__init__(type, *args, **kwargs)
