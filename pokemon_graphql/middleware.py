from .loaders import Loaders

class LoaderMiddleware(object):
    """
	Graphene middleware for attaching a new instance of Loaders to the
	request context.
	"""
    def resolve(self, next, root, info, **args):
        if not hasattr(info.context, "loaders"):
            info.context.loaders = Loaders()
        return next(root, info, **args)
