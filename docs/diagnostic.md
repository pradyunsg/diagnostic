# `diagnostic`

<!--
    This is documented manually, since Sphinx doesn't seem to like dataclasses.
    >.<
-->

```{eval-rst}
.. class:: diagnostic.DiagnosticStyle

    Data about how to present a :class:`Diagnostic` object.

    This is a frozen dataclass, so you can't change the values after creating
    the object and can use it as a key in a dictionary.

    .. method:: __init__(*, name, color, ascii_symbol, unicode_symbol)

        :param name: The name of this style. This is used before the code.
        :type name: str
        :param color: The Rich markup "style" to use.
        :type color: str
        :param ascii_symbol: The symbol to use in an ASCII-only environment.
        :type ascii_symbol: str
        :param unicode_symbol: The symbol to use in a Unicode-capable environment.
        :type unicode_symbol: str
        :rtype: None

    .. attribute:: name
        :type: str

        The name of this style. This is used before the code.

    .. attribute:: color
        :type: str

        The Rich markup "style" to use.

    .. attribute:: ascii_symbol
        :type: str

        The symbol to use in an ASCII-only environment.

    .. attribute:: unicode_symbol
        :type: str

        The symbol to use in a Unicode-capable environment.
```

```{eval-rst}
.. autoclass:: diagnostic.Diagnostic
    :members:
```

```{eval-rst}
.. autoclass:: diagnostic.DiagnosticError
   :show-inheritance:
```

```{eval-rst}
.. autoclass:: diagnostic.DiagnosticWarning
   :show-inheritance:
```
