from _plotly_utils.basevalidators import NumberValidator


class DbValidator(NumberValidator):
    """
    Validateur personnalisé pour la propriété 'db' du composant Plotly 'contourcarpet'.
    Hérite de NumberValidator pour assurer que la valeur est numérique.
    """

    def __init__(
        self,
        plotly_name: str = "db",
        parent_name: str = "contourcarpet",
        **kwargs
    ):
        super().__init__(
            plotly_name=plotly_name,
            parent_name=parent_name,
            edit_type=kwargs.pop("edit_type", "calc"),
            implied_edits=kwargs.pop("implied_edits", {"ytype": "scaled"}),
            **kwargs,
        )
