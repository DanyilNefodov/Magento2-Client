from .attributes import (
    Magento2Attributes,
)
from .categories import (
    Magento2Categories,
)
from .orders import (
    Magento2Orders,
)
from .product_media import (
    Magento2ProductMedia,
)
from .product_stock import (
    Magento2Stock,
)
from .products import (
    Magento2Products,
)
from .stores import (
    Magento2Stores,
)


class Magento2Client(
        Magento2Attributes, Magento2Categories, Magento2Orders,
        Magento2ProductMedia, Magento2Stock, Magento2Products,
        Magento2Stores,
        ):
    pass
