from app.models import ReactionSet

def test_models_instantiates():
    rs = ReactionSet(document_title="x", reactions=[])
    assert rs.document_title == "x"
