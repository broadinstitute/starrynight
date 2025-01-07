"""Starrynight module registry."""

from starrynight.modules.common import StarrynightModule
from starrynight.modules.gen_index import GenIndexModule
from starrynight.modules.gen_inv import GenInvModule

MODULE_REGISTRY: dict[str, type(StarrynightModule)] = {
    GenInvModule.uid(): GenInvModule,
    GenIndexModule.uid(): GenIndexModule,
}
