"""Generic visitor pattern implementation for Python objects."""

import enum


class Visitor(object):

    defaultStop = False

    @classmethod
    def _register(celf, clazzes_attrs):
        assert celf != Visitor, "Subclass Visitor instead."
        if "_visitors" not in celf.__dict__:
            celf._visitors = {}

        def wrapper(method):
            assert method.__name__ == "visit"
            for clazzes, attrs in clazzes_attrs:
                if type(clazzes) != tuple:
                    clazzes = (clazzes,)
                if type(attrs) == str:
                    attrs = (attrs,)
                for clazz in clazzes:
                    _visitors = celf._visitors.setdefault(clazz, {})
                    for attr in attrs:
                        assert (
                            attr not in _visitors
                        ), f"Oops, class '{clazz.__name__}' has visitor function for '{attr}' defined already."
                        _visitors[attr] = method
            return None

        return wrapper

    @classmethod
    def register(cls, clazzes):
        if type(clazzes) != tuple:
            clazzes = (clazzes,)
        return cls._register([(clazzes, (None,))])

    @classmethod
    def register_attr(cls, clazzes, attrs):
        if type(clazzes) != tuple:
            clazzes = (clazzes,)
        if type(attrs) == str:
            attrs = (attrs,)
        clazzes_attrs = [(clazz, attrs) for clazz in clazzes]
        return cls._register(clazzes_attrs)

    @classmethod
    def register_attrs(cls, clazzes_attrs):
        return cls._register(clazzes_attrs)

    @classmethod
    def _visitorsFor(cls, thing, _default={}):
        typ = type(thing)

        for cls in cls.mro():

            _visitors = getattr(cls, "_visitors", None)
            if _visitors is None:
                break

            m = cls._visitors.get(typ, None)
            if m is not None:
                return m

        return _default

    def visitObject(self, obj, *args, **kwargs):
        """Called to visit an object. This function loops over all non-private
        attributes of the objects and calls any user-registered (via
        @register_attr() or @register_attrs()) visit() functions.

        If there is no user-registered visit function, of if there is and it
        returns True, or it returns None (or doesn't return anything) and
        visitor.defaultStop is False (default), then the visitor will proceed
        to call self.visitAttr()"""

        keys = sorted(vars(obj).keys())
        _visitors = self._visitorsFor(obj)
        defaultVisitor = _visitors.get("*", None)
        for key in keys:
            if key[0] == "_":
                continue
            value = getattr(obj, key)
            visitorFunc = _visitors.get(key, defaultVisitor)
            if visitorFunc is not None:
                ret = visitorFunc(self, obj, key, value, *args, **kwargs)
                if ret == False or (ret is None and self.defaultStop):
                    continue
            self.visitAttr(obj, key, value, *args, **kwargs)

    def visitAttr(self, obj, attr, value, *args, **kwargs):
        """Called to visit an attribute of an object."""
        self.visit(value, *args, **kwargs)

    def visitList(self, obj, *args, **kwargs):
        """Called to visit any value that is a list."""
        for value in obj:
            self.visit(value, *args, **kwargs)

    def visitDict(self, obj, *args, **kwargs):
        """Called to visit any value that is a dictionary."""
        for value in obj.values():
            self.visit(value, *args, **kwargs)

    def visitLeaf(self, obj, *args, **kwargs):
        """Called to visit any value that is not an object, list,
        or dictionary."""
        pass

    def visit(self, obj, *args, **kwargs):
        """This is the main entry to the visitor. The visitor will visit object
        obj.

        The visitor will first determine if there is a registered (via
        @register()) visit function for the type of object. If there is, it
        will be called, and (visitor, obj, *args, **kwargs) will be passed to
        the user visit function.

        If there is no user-registered visit function, of if there is and it
        returns True, or it returns None (or doesn't return anything) and
        visitor.defaultStop is False (default), then the visitor will proceed
        to dispatch to one of self.visitObject(), self.visitList(),
        self.visitDict(), or self.visitLeaf() (any of which can be overriden in
        a subclass)."""

        visitorFunc = self._visitorsFor(obj).get(None, None)
        if visitorFunc is not None:
            ret = visitorFunc(self, obj, *args, **kwargs)
            if ret == False or (ret is None and self.defaultStop):
                return
        if hasattr(obj, "__dict__") and not isinstance(obj, enum.Enum):
            self.visitObject(obj, *args, **kwargs)
        elif isinstance(obj, list):
            self.visitList(obj, *args, **kwargs)
        elif isinstance(obj, dict):
            self.visitDict(obj, *args, **kwargs)
        else:
            self.visitLeaf(obj, *args, **kwargs)
