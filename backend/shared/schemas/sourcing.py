from marshmallow import Schema, fields, validate, EXCLUDE

class SupplierSchema(Schema):
    """
    Describes a supplier/manufacturer.
    """
    class Meta:
        unknown = EXCLUDE

    supplier_id = fields.String(required=True)
    name = fields.String(required=True)
    region = fields.String(required=True)

    capabilities = fields.List(
        fields.String(),
        required=True,
        validate=validate.Length(min=1)
    )

    base_unit_cost = fields.Float(required=True)
    base_lead_time_days = fields.Integer(required=True)

    min_total_price = fields.Float(required=True)
    max_total_price = fields.Float(required=True)

    max_lead_time_days = fields.Integer(required=True)

class SourcingResultSchema(Schema):
    """
    Ranked shortlist of suppliers.
    """
    class Meta:
        unknown = EXCLUDE

    request_id = fields.String(required=True)

    heuristic = fields.String(
        required=True,
        validate=validate.OneOf(["cost", "deadline"])
    )

    ranked_suppliers = fields.List(
        fields.Nested(SupplierSchema),
        required=True
    )

    notes = fields.String(allow_none=True)
