
class ChangeLogType:
    ITEM_ADD = 0
    ITEM_DEL = 1
    ITEM_MOD = 2
    VARIANT_ADD = 3
    VARIANT_DEL = 4
    VARIANT_MOD = 5

    Map = {
        ITEM_ADD : 'item_added',
        ITEM_DEL: 'item_deleted',
        ITEM_MOD: 'item_modified',
        VARIANT_ADD: 'variant_added',
        VARIANT_DEL: 'variant_deleted',
        VARIANT_MOD: 'variant_modiied'
    }
