import pytest
import tablib

from sportsbetting.admin.resources import GoverningBodyResource
from sportsbetting.models import GoverningBody, Sport


@pytest.mark.django_db
def test_gb_export_fields():
    sport = Sport.objects.create(name="Soccer")
    gb = GoverningBody.objects.create(sport=sport, name="FIFA", type="int")
    resource = GoverningBodyResource()
    dataset = resource.export()
    headers = dataset.headers
    assert set(["id", "sport", "key", "name", "description", "type"]).issubset(
        set(headers)
    )
    row = list(dataset)[0]
    assert row[headers.index("name")] == "FIFA"
    assert row[headers.index("sport")] == sport.pk


@pytest.mark.django_db
def test_gb_import(tmp_path):
    sport = Sport.objects.create(name="Basketball")
    csv_content = f"id,sport,key,name,description,type\n,{sport.pk},,FIBA,,int\n"
    resource = GoverningBodyResource()
    dataset = tablib.Dataset().load(csv_content, format="csv")
    result = resource.import_data(dataset, dry_run=True)
    assert not result.has_errors()
    result = resource.import_data(dataset, dry_run=False)
    assert not result.has_errors()
    assert GoverningBody.objects.filter(name="FIBA").exists()
