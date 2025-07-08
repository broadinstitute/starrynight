# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
from starrynight.utils.misc import anywidgets_path
from starrynight.schema import DataConfig
from starrynight.modules.gen_index import GenIndexModule
from starrynight.modules.schema import SpecContainer
from psygnal import EventedModel
from anywidget.experimental import widget

import anywidget



# %%
js_path = anywidgets_path().joinpath("App.js")
css_path = anywidgets_path().joinpath("anywidget.css")

# %%
data_config = DataConfig(
    dataset_path="",
    storage_path="",
    workspace_path="",
)

gen_inv_mod = GenIndexModule(data_config)

@widget(esm=js_path.read_text(), css=css_path.read_text())
class CounterWidgetModel(EventedModel):
    spec: SpecContainer


# %%
a = CounterWidgetModel(spec=gen_inv_mod.spec)

# %%
a

# %%
a.spec

# %%
