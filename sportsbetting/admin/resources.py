from import_export import resources
from ..models import GoverningBody

class GoverningBodyResource(resources.ModelResource):
    class Meta:
        model = GoverningBody
        fields = ('id', 'sport', 'key', 'name', 'description', 'type')
        export_order = ('id', 'sport', 'key', 'name', 'description', 'type')
