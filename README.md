This is a Python TUI framework forked from jwlodek/py_cui, but much is changed.

Checkout example/all_in_one.py for usage example. Other examples and unit tests are not maintained.

TODO:
----
- use event-based callback
- implement scrollable-linear-layout
- combined widget = outside controller + layout + inside widget (menu=linear-layout+label, blocktext=scrollable-layout+lineedit)

DONE:
----
- use CSS-like style for widget.
- draw border/decoration and content separately, so the content can be put into another widget.
